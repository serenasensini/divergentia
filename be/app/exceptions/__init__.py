"""Exception handling package"""
from app.exceptions.custom_exceptions import (
    ApplicationException,
    ValidationException,
    FileUploadException,
    FileProcessingException,
    DocumentNotFoundException,
    OllamaConnectionException,
    OllamaProcessingException,
    FormattingException,
    RateLimitExceededException,
    UnauthorizedException
)

__all__ = [
    'ApplicationException',
    'ValidationException',
    'FileUploadException',
    'FileProcessingException',
    'DocumentNotFoundException',
    'OllamaConnectionException',
    'OllamaProcessingException',
    'FormattingException',
    'RateLimitExceededException',
    'UnauthorizedException'
]
