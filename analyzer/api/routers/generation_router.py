import logging
import uuid

from fastapi import APIRouter, HTTPException

from api import logs
from api.ai.generation import *
from api.data.db import *
from api.dto import *


logger = logs.get_logger(__name__)


router = APIRouter(prefix="/generation", tags=["Generation"])


@router.post("/analysis-summary",
          response_model=SummaryResponse,
          description='Generates summary with found vulnerabilities and bad practices.')
def get_code_summary(query_input: SummaryRequest):
    raise HTTPException(status_code=500, detail="Not implemented. Yet.")
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


@router.post("/unit-tests",
          response_model=UnitTestResponse,
          description='Generates source code for unit tests for given source code file.')
def get_unit_tests(request: UnitTestRequest):
    session_id = request.session_id or str(uuid.uuid4())

    rag_chain = get_unit_tests_rag_chain()
    answer = rag_chain.invoke({
        "input": f"strictly follow system instructions and write unit tests for {'all source code in context' if request.request is None else request.request}",
        "language": request.language,
        "framework": request.framework,
    })['answer']

    # markdown stuff
    answer = str.replace(answer, '```', '')

    logger.info(f"SID: {session_id}, Response: {answer}")
    insert_application_logs(session_id, 'unit_tests_request', answer)
    return UnitTestResponse(source_code=answer, session_id=session_id)
