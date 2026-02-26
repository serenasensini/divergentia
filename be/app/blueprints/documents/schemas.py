"""
Pydantic Schemas for Document API
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Response schema for document upload"""
    document_id: str
    original_filename: str
    file_size: int
    mime_type: str
    file_extension: str
    message: str = "Document uploaded successfully"


class TextExtractionResponse(BaseModel):
    """Response schema for text extraction"""
    document_id: str
    text_content: str
    character_count: int
    word_count: int


class FormattingResponse(BaseModel):
    """Response schema for formatting operation"""
    success: bool
    output_path: str
    format: str
    message: Optional[str] = None
    applied_options: Dict[str, Any]


class SummaryResponse(BaseModel):
    """Response schema for document summarization"""
    document_id: str
    document_name: str
    summary: str
    key_points: List[str]
    summary_type: str
    original_length: int
    summary_length: int
    compression_ratio: float


class ParaphraseResponse(BaseModel):
    """Response schema for document paraphrasing"""
    document_id: str
    document_name: str
    style: str
    total_sections: int
    paraphrased_sections: Dict[int, str]


class TextSummaryResponse(BaseModel):
    """Response schema for direct text summarization"""
    summary: str
    original_length: int
    summary_length: int


class TextParaphraseResponse(BaseModel):
    """Response schema for direct text paraphrasing"""
    paraphrased_text: str
    style: str
    original_length: int
    paraphrased_length: int


class HealthCheckResponse(BaseModel):
    """Response schema for health check"""
    status: str
    api_version: str = "1.0.0"
    ollama_status: Dict[str, Any]


class SupportedFormatsResponse(BaseModel):
    """Response schema for supported formats"""
    supported_formats: List[str]
    format_details: Dict[str, Dict[str, Any]]


class ErrorResponse(BaseModel):
    """Response schema for errors"""
    error: str
    message: str
    status_code: int
    details: Optional[Dict[str, Any]] = None
