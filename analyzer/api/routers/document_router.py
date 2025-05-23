from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
from typing import Optional

from api.data.db import *
from api.data.vectorstore import *
from api.data.types import DataType
from api.dto import DocumentInfo

logger = logs.get_logger(__name__)

router = APIRouter(prefix="/project", tags=["Project files"])


async def upload_and_index_document(file: UploadFile, dtype: DataType):
    temp_file_path = f"temp_{file.filename}"

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_id = insert_document_record(file.filename, dtype)
        success = index_document_to_chroma(temp_file_path, file_id, dtype)

        if success:
            return {"message": f"File {file.filename} has been uploaded and indexed.", "file_id": file_id}
        else:
            delete_document_record(file_id, dtype)
            raise HTTPException(status_code=500, detail=f"Failed to index {file.filename}.")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


async def list_documents(dtype: Optional[DataType] = None):
    return get_all_documents(dtype)


async def delete_document(file_id: int, dtype: DataType):
    chroma_delete_success = delete_doc_from_chroma(file_id, dtype)

    if chroma_delete_success:
        db_delete_success = delete_document_record(file_id, dtype)
        if db_delete_success:
            return {"message": f"Deleted document with file_id {file_id} from the system."}
        else:
            return {"error": f"Deleted from Chroma but failed to delete document with file_id {file_id} from the database."}
    else:
        return {"error": f"Failed to delete document with file_id {file_id} from Chroma."}


# Source Code Routes
@router.post("/code",
          description='Uploads source code for project to generate tests and summary for',
          response_model=dict)
async def upload_source_code(file: UploadFile = File(...)):
    return await upload_and_index_document(file, DataType.SOURCE_CODE)


@router.get("/code",
         response_model=list[DocumentInfo],
         description='Returns all uploaded source code documents')
async def get_source_code():
    return await list_documents(DataType.SOURCE_CODE)


@router.delete("/code/{file_id}",
            description='Deletes specified source code file')
async def delete_source_code(file_id: int):
    return await delete_document(file_id, DataType.SOURCE_CODE)


# Requirements Routes
@router.post("/requirements",
          description='Uploads technical requirements document for project to improve tests and summary generation')
async def upload_requirements(file: UploadFile = File(...)):
    return await upload_and_index_document(file, DataType.REQUIREMENTS)


@router.get("/requirements",
         response_model=list[DocumentInfo],
         description='Returns all uploaded technical requirements')
async def get_requirements():
    return await list_documents(DataType.REQUIREMENTS)


@router.delete("/requirements/{file_id}",
            description='Deletes specified technical requirements document')
async def delete_requirements(file_id: int):
    return await delete_document(file_id, DataType.REQUIREMENTS)


# Reports Routes
@router.post("/reports",
          description='Uploads static analysis reports for the project')
async def upload_report(file: UploadFile = File(...)):
    return await upload_and_index_document(file, DataType.REPORTS)


@router.get("/reports",
         response_model=list[DocumentInfo],
         description='Returns all uploaded reports')
async def get_reports():
    return await list_documents(DataType.REPORTS)


@router.delete("/reports/{file_id}",
            description='Deletes specified report document')
async def delete_report(file_id: int):
    return await delete_document(file_id, DataType.REPORTS)
