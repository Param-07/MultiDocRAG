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


def test_image_element_with_asset_reference():
    location = SourceLocation(
        page_number=2,
        bounding_box=(100.0, 150.0, 450.0, 350.0),
        coordinate_system="pdf_points",
        format_specific={"element_type": "image"},
    )

    metadata = ElementExtractionMetadata(
        extraction_method="embedded_image_extraction",
        extractor_name="pymupdf",
        extractor_version="1.26.0",
    )

    element = ExtractedElement(
        element_id="elem_003",
        content_type="image",
        content={
            "asset_reference": "assets/image_003.png",
            "mime_type": "image/png",
        },
        source_location=location,
        extraction_metadata=metadata,
    )

    assert element.content_type == "image"
    assert element.content["asset_reference"] == "assets/image_003.png"
    assert element.content["mime_type"] == "image/png"
    assert element.source_location.page_number == 2



from datetime import datetime, timezone

from app.processing.models.extraction_result import (
    ExtractionResult,
    ExtractionMetadata,
    ExtractionStatus,
)


def test_extraction_result_with_multiple_elements():
    started_at = datetime.now(timezone.utc)

    extraction_metadata = ExtractionMetadata(
        extractor_name="pymupdf",
        extractor_version="1.26.0",
        started_at=started_at,
        completed_at=started_at,
        configuration={},
    )

    text_location = SourceLocation(
        page_number=1,
        bounding_box=(50.0, 100.0, 500.0, 150.0),
        coordinate_system="pdf_points",
    )

    element_metadata = ElementExtractionMetadata(
        extraction_method="native",
        extractor_name="pymupdf",
        extractor_version="1.26.0",
    )

    text_element = ExtractedElement(
        element_id="elem_001",
        content_type="text",
        content={"text": "Annual financial report."},
        source_location=text_location,
        extraction_metadata=element_metadata,
    )

    result = ExtractionResult(
        document_id="doc_001",
        version_id="ver_001",
        processing_run_id="run_001",
        schema_version="1.0.0",
        status=ExtractionStatus.SUCCESS,
        extraction_metadata=extraction_metadata,
        elements=[text_element],
        errors=[],
    )

    assert result.status == ExtractionStatus.SUCCESS
    assert result.document_id == "doc_001"
    assert len(result.elements) == 1
    assert result.elements[0].content["text"] == "Annual financial report."
    assert result.errors == []


from app.processing.models.extraction_result import ExtractionError


def test_partial_success_extraction_result():
    now = datetime.now(timezone.utc)

    result = ExtractionResult(
        document_id="doc_002",
        version_id="ver_002",
        processing_run_id="run_002",
        schema_version="1.0.0",
        status=ExtractionStatus.PARTIAL_SUCCESS,
        extraction_metadata=ExtractionMetadata(
            extractor_name="pymupdf",
            extractor_version="1.26.0",
            started_at=now,
            completed_at=now,
        ),
        elements=[ ExtractedElement(
                element_id="elem_001",
                content_type="text",
                content={"text": "Revenue increased by 15%."},
                source_location=SourceLocation(
                    page_number=3,
                    bounding_box=(50.0, 120.0, 540.0, 200.0),
                    coordinate_system="pdf_points",
                    format_specific={"element_type": "text_block"},
                ),
                extraction_metadata= ElementExtractionMetadata(
                    extraction_method="native",
                    extractor_name="pymupdf",
                    extractor_version="1.26.0",
                ),
            )
        ],
        errors=[
            ExtractionError(
                error_code="IMAGE_EXTRACTION_FAILED",
                message="Unable to extract an embedded image.",
                page_number=4,
                stage="image_extraction",
            )
        ],
    )

    assert result.status == ExtractionStatus.PARTIAL_SUCCESS
    assert len(result.errors) == 1
    assert result.errors[0].page_number == 4
    assert result.errors[0].stage == "image_extraction"
