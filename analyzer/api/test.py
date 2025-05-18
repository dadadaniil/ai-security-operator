# TEST STUFF HERE

from langchain_core.runnables.utils import Output

from api.ai.generation import get_unit_tests_rag_chain

# get_vectorstore(DataType.REPORTS)

chain = get_unit_tests_rag_chain()
out: Output = chain.invoke({
        "input": "What framework should you use to write tests?",
        "language": "C#",
        "framework": "xUnit",
        "chat_history": []
    })
print(out)