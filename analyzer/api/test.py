# TEST STUFF HERE

from langchain_core.runnables.utils import Output
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_unstructured import UnstructuredLoader

from api.ai.generation import get_unit_tests_rag_chain
from api.data.types import DataType
from api.data.vectorstore import index_document_to_chroma

# get_vectorstore(DataType.REPORTS)

file_path = 'test.java'

index_document_to_chroma(file_path, 0, DataType.SOURCE_CODE)


# chain = get_unit_tests_rag_chain()
# out: Output = chain.invoke({
#         "input": "What framework should you use to write tests?",
#         "language": "C#",
#         "framework": "xUnit",
#         "chat_history": []
#     })
# print(out)