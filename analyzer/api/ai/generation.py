from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.retrievers import EnsembleRetriever
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_ollama import ChatOllama

from api.data.types import DataType
from api.data.vectorstore import get_vectorstore
from api.env import *


def __get_retriever(dtype: DataType, num_docs: int) -> VectorStoreRetriever:
    return get_vectorstore(dtype).as_retriever(search_kwargs={"k": num_docs})


# To allow us to change llm provider later
def __get_llm(**kwargs) -> BaseChatModel:
    return ChatOllama(model=LLM_MODEL, num_predict=LLM_OUTPUT_TOKEN_LIMIT, **kwargs)


contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are assistant that analyzes given code for bad practices and security vulnerabilities. "
               "Given source code, find bad practices and security vulnerabilities. "
               "Assume that code is syntactically correct and references only defined symbols. "
               "Ignore suggestions and potential issues. Only list real existing issues. "
               "For each issue double-check step by step if it really exists in code and if it really is a problem using your knowledge of programming language. "
               "Format output as JSON dictionary where vulnerability name is key and description is value. Do not output anything else."),
    ("system", "Context: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

unit_test_writing_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are given source code, technical requirements for code and static analysis reports for code. "
               "Write unit tests for specified feature in source code to cover related technical requirements. "
               "Don't forget about edge cases that may be not present in static analysis reports. "
               "Use {framework} framework for {language} programming language to write unit tests. "
               "Output strictly only source code. Do not output anything else."),
    ("system", "Context: {context}"),
    ("human", "{input}"),
])


def get_analysis_rag_chain() -> Runnable:
    llm = __get_llm(temperature=0.15)

    code_retriever = __get_retriever(DataType.SOURCE_CODE, 20)

    history_aware_retriever = create_history_aware_retriever(llm, code_retriever, contextualize_q_prompt)
    question_answer_chain = create_stuff_documents_chain(llm, analysis_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)    
    return rag_chain


def get_unit_tests_rag_chain() -> Runnable:
    llm = __get_llm(temperature=0.05)

    code_retriever = __get_retriever(DataType.SOURCE_CODE, 10)
    requirements_retriever = __get_retriever(DataType.REQUIREMENTS, 10)

    ensemble_retriever = EnsembleRetriever(
        retrievers=[code_retriever, requirements_retriever], weights=[0.5, 0.5]
    )

    question_answer_chain = create_stuff_documents_chain(llm, unit_test_writing_prompt)
    rag_chain = create_retrieval_chain(ensemble_retriever, question_answer_chain)
    return rag_chain