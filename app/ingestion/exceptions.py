class FileValidationError(Exception):
    """Custom exception for file validation errors."""
    
    def __init__(self, message: str, code: str = "CORRUPTED_FILE", status_code: int = 422):
        super().__init__(message)
        self.code = code
        self.status_code = status_code  
        self.message = message