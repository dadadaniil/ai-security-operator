import logging
from json import load
from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter, RecursiveJsonSplitter
from langchain_unstructured import UnstructuredLoader

from api import logs
from api.data.types import DataType
from api.env import LLM_MODEL, VECTORSTORE_PATH


logger = logs.get_logger(__name__)


supported_extensions = ['.pdf', '.docx', '.html']

__vector_stores: dict[DataType, Chroma] = {}


def get_collection_name(dtype: DataType) -> str:
    return dtype.name


def get_vectorstore(dtype: DataType) -> Chroma:
    if dtype not in __vector_stores:
        vectorstore = Chroma(
            collection_name=get_collection_name(dtype),
            persist_directory=VECTORSTORE_PATH,
            embedding_function=OllamaEmbeddings(model=LLM_MODEL)
        )

        __vector_stores[dtype] = vectorstore

    return __vector_stores[dtype]


def __embed_document(file_path: str) -> List[Document]:
    if file_path.endswith('.json'):
        splitter = RecursiveJsonSplitter(max_chunk_size=500)

        with open(file_path) as f:
            json_data = load(f)
            documents = splitter.create_documents(texts=[json_data])
    else:
        # todo works 50/50, breaks with pdf's obtained via 'print' in chrome. json is fine though
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)

        loader = UnstructuredLoader(file_path)
        loaded = loader.load()
        documents = splitter.split_documents(loaded)

    return documents


def index_document_to_chroma(file_path: str, file_id: int, dtype: DataType) -> bool:
    vectorstore = get_vectorstore(dtype)

    try:
        splits = __embed_document(file_path)

        for split in splits:
            split.metadata['file_id'] = file_id

        vectorstore.add_documents(splits)
        return True
    except Exception as e:
        logger.error(f"Error indexing document: {e}")
        return False


def delete_doc_from_chroma(file_id: int, dtype: DataType) -> bool:
    vectorstore = get_vectorstore(dtype)

    try:
        vectorstore.delete(where={"file_id": file_id})

        remaining = vectorstore.get(where={"file_id": file_id})
        if remaining.get('ids'):
            logger.error(f"Documents remain after deletion for file_id {file_id}")
            return False

        return True

    except Exception as e:
        logger.error(f"Deletion failed: {str(e)}", exc_info=True)
        return False