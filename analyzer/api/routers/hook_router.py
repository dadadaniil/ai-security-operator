from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
from typing import Optional

from api.data.db import *
from api.data.vectorstore import *
from api.data.types import DataType
from api.dto import DocumentInfo

logger = logs.get_logger(__name__)

router = APIRouter(prefix="/hook", tags=["Hooks for GitHub and other services"])


# Source Code Routes
@router.post("/github",
          description='Uploads source code for project to generate tests and summary for',
          response_model=dict)
async def upload_source_code(src):
    logger.info(f"Yay: {str(src)}")
