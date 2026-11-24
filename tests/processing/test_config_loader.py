from pathlib import Path

import pytest

from app.processing.config_loader import load_processing_config
from app.processing.models.processing_config import (
    OCRConfig,
    PDFConfig,
    ProcessingConfig,
    StorageConfig,
)


VALID_CONFIG = """\
storage:
  asset_directory: custom/assets
pdf:
  extract_images: false
  extract_tables: true
  preserve_layout: false
ocr:
  enabled: true
  engine: tesseract
  language: eng
  confidence_threshold: 0.8
"""


def test_load_processing_config_uses_default_configuration():
    config = load_processing_config()

    assert isinstance(config, ProcessingConfig)
    assert isinstance(config.storage, StorageConfig)
    assert config.storage.asset_directory == Path("data/processed/assets")
    assert isinstance(config.pdf, PDFConfig)
    assert config.pdf.extract_images is True
    assert isinstance(config.ocr, OCRConfig)
    assert config.ocr.engine == "tesseract"


def test_load_processing_config_uses_custom_path(tmp_path):
    config_path = tmp_path / "custom_processing.yaml"
    config_path.write_text(VALID_CONFIG, encoding="utf-8")

    config = load_processing_config(config_path)

    assert config.storage.asset_directory == Path("custom/assets")
    assert config.pdf.extract_images is False
    assert config.pdf.extract_tables is True
    assert config.pdf.preserve_layout is False
    assert config.ocr.confidence_threshold == 0.8


def test_load_processing_config_rejects_missing_file(tmp_path):
    config_path = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError):
        load_processing_config(config_path)


def test_load_processing_config_rejects_invalid_yaml(tmp_path):
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text("storage: [invalid", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid YAML"):
        load_processing_config(config_path)


def test_load_processing_config_rejects_empty_yaml(tmp_path):
    config_path = tmp_path / "empty.yaml"
    config_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="YAML mapping"):
        load_processing_config(config_path)


def test_load_processing_config_rejects_invalid_values(tmp_path):
    config_path = tmp_path / "invalid_values.yaml"
    config_path.write_text(
        VALID_CONFIG.replace("confidence_threshold: 0.8", "confidence_threshold: 1.1"),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid processing configuration"):
        load_processing_config(config_path)
