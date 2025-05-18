import logging
from typing import List

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from api.data.types import DataType
from api.env import LLM_MODEL, VECTORSTORE_PATH

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


supported_extensions = ['.pdf', '.docx', '.html']

__text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
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


# todo HTML can not be indexed, why
# todo embed plain text
def embed_document(file_path: str) -> List[Document]:
    # todo map instead of ifs
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith('.html'):
        loader = UnstructuredHTMLLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    documents = loader.load()
    return __text_splitter.split_documents(documents)


def index_document_to_chroma(file_path: str, file_id: int, dtype: DataType) -> bool:
    vectorstore = get_vectorstore(dtype)

    try:
        splits = embed_document(file_path)

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