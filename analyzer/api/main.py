import json

import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
import os
import uuid
import logging
import shutil

from fastapi.openapi.utils import get_openapi

from api.chroma_utils import *
from api.db_utils import *
from api.langchain_utils import *
from api.pydantic_models import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(levelname)s %(asctime)s %(name)s - %(message)s", "%H:%M:%S")

file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Code Analyzer API",
        version="1.0.0",
        description="API for vulnerability analysis and test writing",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", "8000"))
    logger.info(f"Documentation available at http://127.0.0.1:{port}/docs")
    uvicorn.run("main:app", host="127.0.0.1", port=port)


# Generation

# todo what if codebase is too large? how to specify exact module for summary
@app.get("/analyzer/summary",
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
@app.get("/testwriter/unit",
          response_model=UnitTestResponse,
          description='Generates source code for unit tests for given source code file.')
def get_unit_tests(request: UnitTestRequest):
    pass
    # session_id = request.session_id or str(uuid.uuid4())
    #
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



# Source code

@app.post("/project/code",
          description='Uploads source code for project to generate tests and summary for')
def upload_source_code(file: UploadFile = File(...)):
    pass

@app.get("/project/code",
         response_model=list[DocumentInfo],
         description='Returns all uploaded source code documents')
def get_source_code():
    pass

@app.delete("/project/code/{id}",
            description='Deletes specified source code file')
def delete_source_code(id: uuid.UUID):
    pass



# Requirements

@app.post("/project/requirements",
          description='Uploads technical requirements document for project to improve tests and summary generation')
def upload_code(file: UploadFile = File(...)):
    pass

@app.get("/project/requirements",
         response_model=list[DocumentInfo],
         description='Returns all uploaded technical requirements')
def get_requirements():
    pass

@app.delete("/project/requirements/{id}",
            description='Deletes specified technical requirements document')
def delete_requirements(id: uuid.UUID):
    pass



# Static analysis results

# todo how to link to specific source files? if needed, ofc
@app.post("/project/requirements",
          description='Uploads technical requirements document for project to improve tests and summary generation')
def upload_report(file: UploadFile = File(...)):
    pass

@app.get("/project/requirements",
         response_model=list[DocumentInfo],
         description='Returns all uploaded technical requirements')
def get_reports():
    pass

@app.delete("/project/requirements/{id}",
            description='Deletes specified technical requirements document')
def delete_report(id: uuid.UUID):
    pass




# todo legacy, refactor
def upload_and_index_document(file: UploadFile = File(...)):
    allowed_extensions = ['.pdf', '.docx', '.html']
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}")

    temp_file_path = f"temp_{file.filename}"

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_id = insert_document_record(file.filename)
        success = index_document_to_chroma(temp_file_path, file_id)

        if success:
            return {"message": f"File {file.filename} has been successfully uploaded and indexed.", "file_id": file_id}
        else:
            delete_document_record(file_id)
            raise HTTPException(status_code=500, detail=f"Failed to index {file.filename}.")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# todo legacy, refactor
def list_documents():
    return get_all_documents()


# todo legacy, refactor
def delete_document(file_id: int):
    chroma_delete_success = delete_doc_from_chroma(file_id)

    if chroma_delete_success:
        db_delete_success = delete_document_record(file_id)
        if db_delete_success:
            return {"message": f"Successfully deleted document with file_id {file_id} from the system."}
        else:
            return {"error": f"Deleted from Chroma but failed to delete document with file_id {file_id} from the database."}
    else:
        return {"error": f"Failed to delete document with file_id {file_id} from Chroma."}
