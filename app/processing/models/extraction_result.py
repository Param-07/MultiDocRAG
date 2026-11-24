
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

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

    @model_validator(mode="after")
    def validate_extraction_consistency(self):
        if self.status == ExtractionStatus.SUCCESS:
            if self.errors:
                raise ValueError("A successfull extraction cannot contains errors")

        elif self.status == ExtractionStatus.PARTIAL_SUCCESS:
            if not self.elements:
                raise ValueError("A partially successfull extraction must contain at least one extracted element")
            if not self.errors:
                raise ValueError("A partially successfull extraction must contain at least one error")

        else:
            if self.elements:
                raise ValueError("A failed extraction cannot have any usable extracted element")
            if not self.errors:
                raise ValueError("A failed extraction must have at least one error")

        return self
