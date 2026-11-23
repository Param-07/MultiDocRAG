
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.processing.models.source_location import SourceLocation


class ElementExtractionMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    extraction_method: str
    extractor_name: str | None = None
    extractor_version: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    issues: list[str] = Field(default_factory=list)


class ExtractedElement(BaseModel):
    model_config = ConfigDict(extra="forbid")

    element_id: str
    content_type: Literal["text", "table", "image", "chart"]
    content: dict[str, Any]
    source_location: SourceLocation
    extraction_metadata: ElementExtractionMetadata
