from pathlib import Path
import yaml
from pydantic import ValidationError

from .models.processing_config import ProcessingConfig

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT/"configs"/"processing.yaml"

def load_processing_config(config_path: Path | None = None) -> ProcessingConfig:

    path = config_path if config_path is not None else DEFAULT_CONFIG_PATH

    if not path.is_file():
        raise FileNotFoundError(
            f"Processing config cannot be found at location {path}"
        )

    try:
        with path.open("r", encoding="utf-8") as confg_file:
            config_data = yaml.safe_load(confg_file)
    except yaml.YAMLError as exc:
        raise ValueError(
            f"Invalid YAMLin processing config: {path}"
        )from exc

    if not isinstance(config_data, dict):
        raise ValueError(
            "Processing configuration must contain a YAML mapping "
            "and cannot be empty."
        )

    try:
        return ProcessingConfig.model_validate(config_data)

    except ValidationError as exc:
        raise ValueError(
            f"Invalid processing configuration: {exc}"
        ) from exc