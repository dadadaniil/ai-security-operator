import json
import logging
import uuid

from fastapi import APIRouter, HTTPException

from api import logs
from api.ai.generation import *
from api.data.db import *
from api.dto import *


logger = logs.get_logger(__name__)


router = APIRouter(prefix="/generation", tags=["Generation"])


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


@router.post("/relevant-modules",
          response_model=RelevantModulesResponse,
          description='Finds relevant modules to try to apply to project.')
def get_unit_tests(request: RelevantModulesRequest):
    session_id = request.session_id or str(uuid.uuid4())

    rag_chain = get_relevant_modules_rag_chain()
    answer = rag_chain.invoke({
        "input": f"strictly follow system instructions and write list of modules for security testing given project",
        "modules": str(request.modules),
    })['answer']

    # markdown stuff
    answer = str.replace(answer, '```', '')

    logger.info(f"SID: {session_id}, Response: {answer}")
    insert_application_logs(session_id, 'relevant_modules_request', answer)

    list_ = json.loads(answer)
    return RelevantModulesResponse(modules=list_, session_id=session_id)


@router.post("/attack-plan",
          response_model=AttackPlanResponse,
          description='Generate attack plan to apply to project.')
def get_attack_plan(request: AttackPlanRequest):
    session_id = request.session_id or str(uuid.uuid4())

    rag_chain = get_attack_plan_rag_chain()
    answer = rag_chain.invoke({
        "input": f"strictly follow system instructions and write attack plan for security testing given project",
        "modules": str(request.modules),
    })['answer']

    # markdown stuff
    answer = str.replace(answer, '```', '')

    logger.info(f"SID: {session_id}, Response: {answer}")
    insert_application_logs(session_id, 'attack_plan_request', answer)

    plan_ = # todo
    return AttackPlanResponse(plan=plan_, session_id=session_id)
