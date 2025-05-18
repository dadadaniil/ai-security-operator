from pydantic import BaseModel, Field
from datetime import datetime


class DocumentInfo(BaseModel):
    id: int
    filename: str
    upload_timestamp: datetime


class SummaryRequest(BaseModel):
    session_id: str = Field(default=None)


class SummaryResponse(BaseModel):
    session_id: str = Field(default=None)
    summary: dict[str, str]


class UnitTestRequest(BaseModel):
    session_id: str = Field(default=None)
    language: str
    framework: str


class UnitTestResponse(BaseModel):
    session_id: str = Field(default=None)
    source_code: str
