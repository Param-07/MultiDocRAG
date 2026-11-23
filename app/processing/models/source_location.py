from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class SourceLocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page_number: int | None = Field(default= None, description="The page number of the source location.", ge= 1)
    bounding_box: tuple[float, float, float, float] | None = Field(default= None, description="The bounding box of the source location in the format (x_min, y_min, x_max, y_max).")
    coordinate_system: str | None = Field(default= None, description="The coordinate system used for the bounding box. For example, 'pixels', 'inches', 'centimeters', etc.")
    format_specific: dict[str, Any] | None = Field(default= None, description="A dictionary containing format-specific information about the source location. This can include any additional metadata that is relevant to the specific format of the source document.")