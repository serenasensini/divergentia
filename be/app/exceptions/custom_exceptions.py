"""
Custom Application Exceptions
"""
from typing import Optional, Dict, Any


class ApplicationException(Exception):
    """Base exception class for all application exceptions"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        payload: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize application exception.

        Args:
            message: Error message
            status_code: HTTP status code
            payload: Additional error information
        """
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for JSON response.

        Returns:
            Dictionary with error details
        """
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'status_code': self.status_code,
            **self.payload
        }


class ValidationException(ApplicationException):
    """Exception raised for validation errors"""

    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, payload=payload)


class FileUploadException(ApplicationException):
    """Exception raised for file upload errors"""

    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, payload=payload)


class FileProcessingException(ApplicationException):
    """Exception raised for file processing errors"""

    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, payload=payload)


class DocumentNotFoundException(ApplicationException):
    """Exception raised when document is not found"""

    def __init__(self, document_id: str):
        super().__init__(
            f"Document with ID '{document_id}' not found",
            status_code=404,
            payload={'document_id': document_id}
        )


class OllamaConnectionException(ApplicationException):
    """Exception raised for Ollama connection errors"""

    def __init__(self, message: str = "Failed to connect to Ollama service"):
        super().__init__(message, status_code=503)


class OllamaProcessingException(ApplicationException):
    """Exception raised for Ollama processing errors"""

    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, payload=payload)


class FormattingException(ApplicationException):
    """Exception raised for document formatting errors"""

    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, payload=payload)


class RateLimitExceededException(ApplicationException):
    """Exception raised when rate limit is exceeded"""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class UnauthorizedException(ApplicationException):
    """Exception raised for unauthorized access"""

    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, status_code=401)
