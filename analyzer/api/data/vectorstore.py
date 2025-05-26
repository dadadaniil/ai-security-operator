import json
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
        return _process_json_file(file_path)
    else:
        return _process_text_file(file_path)


def _process_json_file(file_path: str) -> List[Document]:
    with open(file_path, encoding='utf-8') as f:
        json_data = json.load(f)

    splitter = RecursiveJsonSplitter(
        max_chunk_size=800
    )

    return splitter.create_documents(texts=[json_data])


def _process_text_file(file_path: str) -> List[Document]:
    loader = UnstructuredLoader(file_path)
    loaded = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=250,
        length_function=len
    )

    return splitter.split_documents(loaded)


def index_document_to_chroma(file_path: str, file_id: int, dtype: DataType) -> bool:
    vectorstore = get_vectorstore(dtype)

    try:
        splits = __embed_document(file_path)

        for split in splits:
            # some weird stuff with lists in metadata
            for k, v in split.metadata.items():
                if isinstance(v, list):
                    split.metadata[k] = str(v)

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