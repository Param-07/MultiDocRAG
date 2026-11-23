
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.processing.models.extracted_element import ExtractedElement


class ExtractionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"


class ExtractionMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    extractor_name: str
    extractor_version: str
    started_at: datetime
    completed_at: datetime | None = None
    configuration: dict = Field(default_factory=dict)


class ExtractionError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error_code: str
    message: str
    page_number: int | None = None
    stage: str


class ExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str
    version_id: str
    processing_run_id: str
    schema_version: str

    status: ExtractionStatus

    extraction_metadata: ExtractionMetadata

    elements: list[ExtractedElement] = Field(default_factory=list)
    errors: list[ExtractionError] = Field(default_factory=list)
