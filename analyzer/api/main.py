import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from api import logs
from api.env import API_PORT
from api.routers import document_router, generation_router, hook_router

logger = logs.get_logger(__name__)

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
app.include_router(hook_router.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)
