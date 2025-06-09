from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Any, Dict, Union, Annotated
from dataclasses import dataclass


class DocumentInfo(BaseModel):
    id: int
    filename: str
    upload_timestamp: datetime


class SummaryRequest(BaseModel):
    request: str | None
    session_id: str = Field(default=None)


class SummaryResponse(BaseModel):
    session_id: str = Field(default=None)
    summary: dict[str, str]


class UnitTestRequest(BaseModel):
    session_id: str = Field(default=None)
    request: str | None = Field(default='Tested feauture description')
    language: str = Field(default='Java')
    framework: str = Field(default='Any')

class UnitTestResponse(BaseModel):
    session_id: str = Field(default=None)
    source_code: str


class RelevantModulesRequest(BaseModel):
    session_id: str = Field(default=None)
    modules: list[str] = Field()

class RelevantModulesResponse(BaseModel):
    session_id: str = Field(default=None)
    modules: list[str] = Field()


class AttackPlanRequest(BaseModel):
    session_id: str = Field(default=None)
    modules: list[str] = Field()

class StepExecutionResult(BaseModel):
    step_id: str
    tool_used: str
    status: str
    message: str
    raw_request: Any
    raw_response: Any
    extracted_data: Dict
    execution_time_ms: float

class AttackPlanExecutionReport(BaseModel):
    plan_id: str
    overall_status: str
    step_results: List[StepExecutionResult]
    start_time: datetime
    end_time: datetime

@dataclass
class MetasploitInstructions:
    tool_type: str = "metasploit"
    module_name: str
    options: Dict[str, Any]

class FuzzerInstructions(BaseModel):
    tool_type: str = "fuzzer"
    target_endpoint: str
    fuzzing_parameters: Dict[str, Any]

ExploitInstructionTypes = Annotated[
    Union[
        MetasploitInstructions,
        FuzzerInstructions
    ],
    Field(discriminator="tool_type")
]

@dataclass
class AttackStep:
    step_id: str
    description: str
    tool_to_use: str
    exploit_instructions: MetasploitInstructions
    expected_result_criteria: Dict

@dataclass
class AttackPlan:
    plan_id: str
    target_info: Dict
    steps: List[AttackStep]

class AttackPlanResponse(BaseModel):
    session_id: str = Field(default=None)
    plan: AttackPlanExecutionReport

