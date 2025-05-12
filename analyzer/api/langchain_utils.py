from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from api.chroma_utils import vectorstore

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

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
    ("system", "You are assistant that writes unit tests for code with vulnerabilities and bad practices. "
               "You are given source code and list of found vulnerabilities and bad practices. "
               "Write unit tests for code to cover potential edge cases. Emphasise provided found bad practices and cover respective code lines with tests. "
               "Don't forget about other edge cases that may be not present in bad practices list. If there are not cases that should be covered by tests, respond with empty string. "
               "Use {framework} framework for {language} programming language to write unit tests. "
               "Format output as plain text source code. Do not output anything else."),
    ("system", "Context: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])


def get_analysis_rag_chain(model: str):
    llm = ChatOllama(model=model, temperature=0.15)
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    question_answer_chain = create_stuff_documents_chain(llm, analysis_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)    
    return rag_chain


def get_unit_tests_rag_chain(model: str):
    llm = ChatOllama(model=model, temperature=0.05)
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    question_answer_chain = create_stuff_documents_chain(llm, unit_test_writing_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    return rag_chain