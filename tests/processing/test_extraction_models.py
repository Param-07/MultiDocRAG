from app.processing.models.source_location import SourceLocation
from app.processing.models.extracted_element import (
    ExtractedElement,
    ElementExtractionMetadata,
)


def test_text_element_with_pdf_source_location():
    location = SourceLocation(
        page_number=3,
        bounding_box=(50.0, 120.0, 540.0, 200.0),
        coordinate_system="pdf_points",
        format_specific={"element_type": "text_block"},
    )

    metadata = ElementExtractionMetadata(
        extraction_method="native",
        extractor_name="pymupdf",
        extractor_version="1.26.0",
    )

    element = ExtractedElement(
        element_id="elem_001",
        content_type="text",
        content={"text": "Revenue increased by 15%."},
        source_location=location,
        extraction_metadata=metadata,
    )

    assert element.content_type == "text"
    assert element.content["text"] == "Revenue increased by 15%."
    assert element.source_location.page_number == 3
    assert element.source_location.bounding_box == (
        50.0, 120.0, 540.0, 200.0
    )
    assert element.source_location.format_specific == {"element_type": "text_block"}