from pydantic import BaseModel, Field
from datetime import datetime


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

class AttackPlanResponse(BaseModel):
    session_id: str = Field(default=None)
    plan:  = Field() # todo
