from fastapi import APIRouter

from api.dto import *

router = APIRouter(prefix="/generation", tags=["Generation"])


# todo what if codebase is too large? how to specify exact module for summary
@router.get("/analyzer/summary",
          response_model=SummaryResponse,
          description='Generates summary with found vulnerabilities and bad practices.')
def get_code_summary(query_input: SummaryRequest):
    pass
    # session_id = query_input.session_id or str(uuid.uuid4())
    #
    # chat_history = get_chat_history(session_id)
    # rag_chain = get_analysis_rag_chain(query_input.model.value)
    # answer = rag_chain.invoke({
    #     "input": query_input.source_code,
    #     "chat_history": chat_history
    # })['answer']
    #
    # # markdown stuff
    # summary_str = str.replace(answer, '```', '')
    # summary = json.loads(summary_str)
    #
    # insert_application_logs(session_id, query_input.source_code, answer, query_input.model.value)
    # logger.info(f"SID: {session_id}, Response: {summary}")
    # return SummaryResponse(summary=summary, session_id=session_id, model=query_input.model)


# todo what if codebase is too large? how to specify exact module for test writing
@router.get("/testwriter/unit",
          response_model=UnitTestResponse,
          description='Generates source code for unit tests for given source code file.')
def get_unit_tests(request: UnitTestRequest):
    pass
    # session_id = request.session_id or str(uuid.uuid4())

    # chat_history = get_chat_history(session_id)
    # rag_chain = get_analysis_rag_chain(request.model.value)
    # answer = rag_chain.invoke({
    #     "input": request.question,
    #     "language": request.language,
    #     "framework": request.framework,
    #     "chat_history": chat_history
    # })['answer']
    #
    # insert_application_logs(session_id, request.source_code, answer, request.model.value)
    # logger.info(f"SID: {session_id}, Response: {answer}")
    # return UnitTestResponse(source_code=answer, session_id=session_id, model=request.model)
