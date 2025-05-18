import logging

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from api.env import API_PORT
from api.routers import document_router, generation_router

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
app.include_router(document_router.router)
app.include_router(generation_router.router)


if __name__ == "__main__":
    port = API_PORT
    logger.info(f"Documentation available at http://127.0.0.1:{port}/docs")
    uvicorn.run("main:app", host="127.0.0.1", port=port)

