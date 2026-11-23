from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.ingestion.validators.file_validator import validate_uploaded_file
from app.ingestion.exceptions import FileValidationError

router = APIRouter()

@router.post("/")
async def upload_document(
    file: UploadFile = File(...),
    metadata: str | None = Form(None),
    document_id: str | None = Form(None),
):
    """
    Endpoint to upload a document along with its metadata.
    """
    # Here you can process the uploaded file and metadata as needed
    # For demonstration, we'll just return the filename and metadata

    try:
        validate_uploaded_file(file)
    except FileValidationError as e:
        return JSONResponse(status_code=e.status_code, content={"error": e.message})
    return JSONResponse(content={"filename": file.filename, "metadata": metadata})

