"""Utils package"""
from app.utils.file_handler import (
    validate_file,
    save_uploaded_file,
    detect_mime_type,
    get_file_size,
    delete_file,
    sanitize_filename
)
from app.utils.text_extractor import (
    extract_text_from_file,
    count_words,
    count_sentences,
    get_text_preview
)
from app.utils.validators import (
    validate_schema,
    validate_document_id,
    FormattingOptionsSchema,
    SummarizeRequestSchema,
    ParaphraseRequestSchema,
    TextSummarizeRequestSchema,
    TextParaphraseRequestSchema
)

__all__ = [
    'validate_file',
    'save_uploaded_file',
    'detect_mime_type',
    'get_file_size',
    'delete_file',
    'sanitize_filename',
    'extract_text_from_file',
    'count_words',
    'count_sentences',
    'get_text_preview',
    'validate_schema',
    'validate_document_id',
    'FormattingOptionsSchema',
    'SummarizeRequestSchema',
    'ParaphraseRequestSchema',
    'TextSummarizeRequestSchema',
    'TextParaphraseRequestSchema'
]
