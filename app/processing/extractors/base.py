from abc import ABC, abstractmethod
from pathlib import Path

from ..models.extraction_result import ExtractionResult

class BaseExtractor(ABC):

    @abstractmethod # every extractor must implement both methods
    def supports(self, file_path: Path) -> bool:
        """Return whether this extractor supports the given file."""
        pass

    def extract(self, file_path: Path, document_id: str, version_id: str, processing_run_id: str) -> ExtractionResult:
        """Extract content and return a structured extraction result."""
        pass