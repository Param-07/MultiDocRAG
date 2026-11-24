from pathlib import Path

import pytest
from pydantic import ValidationError

from app.processing.models.processing_config import (
    OCRConfig,
    PDFConfig,
    ProcessingConfig,
    StorageConfig,
)


def test_processing_config_accepts_nested_configuration():
    config = ProcessingConfig(
        storage={"asset_directory": "data/processed/assets"},
        pdf={
            "extract_images": False,
            "extract_tables": False,
            "preserve_layout": False,
        },
        ocr={
            "enabled": False,
            "engine": "easyocr",
            "language": "deu",
            "confidence_threshold": 0.85,
        },
    )

    assert isinstance(config.storage, StorageConfig)
    assert config.storage.asset_directory == Path("data/processed/assets")
    assert isinstance(config.pdf, PDFConfig)
    assert config.pdf.extract_images is False
    assert config.pdf.extract_tables is False
    assert config.pdf.preserve_layout is False
    assert isinstance(config.ocr, OCRConfig)
    assert config.ocr.enabled is False
    assert config.ocr.engine == "easyocr"
    assert config.ocr.language == "deu"
    assert config.ocr.confidence_threshold == 0.85


def test_processing_config_defaults():
    config = ProcessingConfig(
        storage={"asset_directory": "assets"},
        pdf={},
        ocr={},
    )

    assert config.pdf.extract_images is True
    assert config.pdf.extract_tables is True
    assert config.pdf.preserve_layout is True
    assert config.ocr.enabled is True
    assert config.ocr.engine == "tesseract"
    assert config.ocr.language == "eng"
    assert config.ocr.confidence_threshold == 0.70


def test_processing_config_requires_storage():
    with pytest.raises(ValidationError):
        ProcessingConfig(pdf={}, ocr={})


@pytest.mark.parametrize(
    ("model", "field"),
    [
        (PDFConfig, "extract_images"),
        (PDFConfig, "extract_tables"),
        (PDFConfig, "preserve_layout"),
        (OCRConfig, "enabled"),
    ],
)
@pytest.mark.parametrize("value", [True, False])
def test_boolean_settings_accept_true_and_false(model, field, value):
    config = model(**{field: value})

    assert getattr(config, field) is value


@pytest.mark.parametrize("threshold", [-0.01, 1.01])
def test_ocr_config_rejects_confidence_outside_unit_interval(threshold):
    with pytest.raises(ValidationError):
        OCRConfig(confidence_threshold=threshold)


@pytest.mark.parametrize("threshold", [0.0, 0.70, 1.0])
def test_ocr_config_accepts_confidence_at_boundaries(threshold):
    config = OCRConfig(confidence_threshold=threshold)

    assert config.confidence_threshold == threshold


@pytest.mark.parametrize(
    ("model", "payload"),
    [
        (StorageConfig, {"asset_directory": "assets", "unknown": True}),
        (PDFConfig, {"extract_images": True, "unknown": True}),
        (OCRConfig, {"engine": "tesseract", "unknown": True}),
        (
            ProcessingConfig,
            {
                "storage": {"asset_directory": "assets"},
                "pdf": {},
                "ocr": {},
                "unknown": True,
            },
        ),
    ],
)
def test_processing_config_models_reject_unknown_fields(model, payload):
    with pytest.raises(ValidationError):
        model(**payload)
