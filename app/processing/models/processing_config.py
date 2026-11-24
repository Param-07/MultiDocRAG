from pydantic import Field, BaseModel, ConfigDict
from pathlib import Path

class StorageConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset_directory: Path

class PDFConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    extract_images: bool = Field(default=True)
    extract_tables: bool = Field(default=True)
    preserve_layout: bool = Field(default=True)

class OCRConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(default=True)
    engine: str = Field(default="tesseract")
    language: str = Field(default="eng")
    confidence_threshold: float = Field(default=0.70, ge=0.0, le=1.0)

class ProcessingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    storage: StorageConfig
    pdf: PDFConfig
    ocr: OCRConfig
