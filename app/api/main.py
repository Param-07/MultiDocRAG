from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import documents

from app.ingestion.exceptions import FileValidationError

app = FastAPI(
    title="Multi-Doc RAG API",
    description="An API for multi-document retrieval-augmented generation (RAG) using FastAPI.",
    version="1.0.0",
)

app.include_router(
    documents.router,
    prefix="/api/v1/documents",
    tags=["Documents"]
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

@app.exception_handler(FileValidationError)
async def file_validation_exception_handler(request, exc: FileValidationError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {
            "code": exc.code,
            "message": exc.message
        }},
    )