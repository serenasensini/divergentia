"""
Document API Routes
"""
import logging
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.exceptions import BadRequest

from app import limiter
from app.services.document_service import get_document_service
from app.services.ollama_service import get_ollama_service
from app.services.formatting_service import get_formatting_service
from app.utils.file_handler import validate_file, save_uploaded_file, detect_mime_type, get_file_size
from app.utils.validators import (
    validate_schema,
    validate_document_id,
    FormattingOptionsSchema,
    FramingOptionsSchema,
    SummarizeRequestSchema,
    ParaphraseRequestSchema,
    TextSummarizeRequestSchema,
    TextParaphraseRequestSchema,
    SpacingOptionsSchema,
    KeywordOptionsSchema
)
from app.exceptions.custom_exceptions import (
    FileUploadException,
    ValidationException
)

logger = logging.getLogger(__name__)

# Create blueprint
documents_bp = Blueprint('documents', __name__)


@documents_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns:
        JSON response with health status

    Example Response:
        {
            "status": "healthy",
            "api_version": "1.0.0",
            "ollama_status": {...}
        }
    """
    logger.info("Health check requested")

    ollama_service = get_ollama_service()
    ollama_status = ollama_service.health_check()

    return jsonify({
        'status': 'healthy',
        'api_version': '1.0.0',
        'ollama_status': ollama_status
    }), 200


@documents_bp.route('/formats/supported', methods=['GET'])
def get_supported_formats():
    """
    Get list of supported file formats.

    Returns:
        JSON response with supported formats

    Example Response:
        {
            "supported_formats": ["pdf", "docx", "txt"],
            "format_details": {...}
        }
    """
    logger.info("Supported formats requested")

    formatting_service = get_formatting_service()

    format_details = {}
    for format_type in ['docx', 'pdf', 'txt']:
        format_details[format_type] = formatting_service.get_available_styles(format_type)

    return jsonify({
        'supported_formats': list(current_app.config['ALLOWED_EXTENSIONS']),
        'format_details': format_details
    }), 200


@documents_bp.route('/documents/upload', methods=['POST'])
@limiter.limit("20 per minute")
def upload_document():
    """
    Upload a document.

    Request:
        - multipart/form-data with 'file' field

    Returns:
        JSON response with document metadata

    Example Response:
        {
            "document_id": "uuid",
            "original_filename": "document.pdf",
            "file_size": 12345,
            "mime_type": "application/pdf",
            "file_extension": "pdf",
            "message": "Document uploaded successfully"
        }
    """
    logger.info("Document upload requested")

    # Check if file is present
    if 'file' not in request.files:
        raise FileUploadException("No file provided in request")

    file = request.files['file']

    if file.filename == '':
        raise FileUploadException("No file selected")

    # Validate file
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning

    is_valid, error_message = validate_file(file.filename, file_size)
    if not is_valid:
        raise FileUploadException(error_message)

    # Save file
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path, original_filename = save_uploaded_file(file, upload_folder)

    # Detect MIME type
    mime_type = detect_mime_type(file_path)

    # Create document record
    document_service = get_document_service()
    document = document_service.create_document(
        file_path=file_path,
        original_filename=original_filename,
        file_size=file_size,
        mime_type=mime_type
    )

    logger.info(f"Document uploaded successfully: {document['id']}")

    return jsonify({
        'document_id': document['id'],
        'original_filename': document['original_filename'],
        'file_size': document['file_size'],
        'mime_type': document['mime_type'],
        'file_extension': document['file_extension'],
        'message': 'Document uploaded successfully'
    }), 201


@documents_bp.route('/documents/<document_id>/extract-text', methods=['POST'])
def extract_text(document_id: str):
    """
    Extract text from document.

    Args:
        document_id: Document ID

    Returns:
        JSON response with extracted text

    Example Response:
        {
            "document_id": "uuid",
            "text_content": "Extracted text...",
            "character_count": 1234,
            "word_count": 200
        }
    """
    logger.info(f"Text extraction requested for document {document_id}")

    validate_document_id(document_id)

    document_service = get_document_service()
    result = document_service.extract_text(document_id)

    return jsonify(result), 200

@documents_bp.route('/documents/<document_id>/format', methods=['PUT'])
def apply_formatting(document_id: str):
    """
    Apply formatting to document parts.

    Args:
        document_id: Document ID

    Request Body:
        {
	"formatting": {
		"titles": false,
		"paragraphs": false,
		"paragraphs_titles": false,
		"captions": false,
		"bibliography": false,
		"theme": {
		  "red_green": {
			"positive": "#00FF00",
			"negative": "#FF0000"
		  },
		  "blue_orange": {
			"positive": "#FFA500",
			"negative": "#0000FF"
		  },
		  "purple_yellow": {
			"positive": "#FFFF00",
			"negative": "#800080"
		    }
		    }
          }
        }

    Returns:
        JSON response with formatted result

    Example Response:
        {
            "success": true,
            "output_path": "/path/to/edited_document.docx",
            "format": "docx",
            "borders_applied": 5,
            "formatting_options": {...}
        }
    """
    logger.info(f"Formatting requested for document {document_id}")

    validate_document_id(document_id)

    # Validate request data
    data = request.get_json()
    if not data:
        raise ValidationException("Request body is required")

    if 'formatting' not in data:
        raise ValidationException("'formatting' field is required in request body")

    validated_data = validate_schema(FormattingOptionsSchema, data['formatting'])
    logger.debug(f"Validated formatting options: {validated_data.dict()}")

    # Apply framing
    document_service = get_document_service()
    output_folder = current_app.config['OUTPUT_FOLDER']

    result = document_service.apply_formatting(
        document_id=document_id,
        formatting_options=validated_data.dict(),
        output_folder=output_folder
    )

    return jsonify(result), 200

@documents_bp.route('/documents/<document_id>/framing', methods=['PUT'])
def apply_framing(document_id: str):
    """
    Apply framing (borders) to document parts.

    Args:
        document_id: Document ID

    Request Body:
        {
	"framing": {
		"sections": false,
		"paragraphs": false,
		"subparagraphs": false,
		"sentences": false,
		"colour": ""
	},
	"text_coloring": {
		"enabled": false,
		"titles": false,
		"paragraphs": false,
		"paragraphs_titles": false,
		"captions": false,
		"bibliography": false,
		"theme": {
		  "red_green": {
			"positive": "#00FF00",
			"negative": "#FF0000"
		  },
		  "blue_orange": {
			"positive": "#FFA500",
			"negative": "#0000FF"
		  },
		  "purple_yellow": {
			"positive": "#FFFF00",
			"negative": "#800080"
		  }
		}
  }
}

    Returns:
        JSON response with framing result

    Example Response:
        {
            "success": true,
            "output_path": "/path/to/edited_document.docx",
            "format": "docx",
            "borders_applied": 5,
            "framing_options": {...}
        }
    """
    logger.info(f"Framing requested for document {document_id}")

    validate_document_id(document_id)

    # Validate request data
    data = request.get_json()
    if not data:
        raise ValidationException("Request body is required")

    if 'framing' not in data:
        raise ValidationException("'framing' field is required in request body")

    validated_data = validate_schema(FramingOptionsSchema, data['framing'])

    # Apply framing
    document_service = get_document_service()
    output_folder = current_app.config['OUTPUT_FOLDER']

    result = document_service.apply_framing(
        document_id=document_id,
        framing_options=validated_data.dict(),
        output_folder=output_folder
    )

    return jsonify(result), 200

@documents_bp.route('/documents/<document_id>/spacing', methods=['PUT'])
def apply_spacing(document_id: str):
    """
    Add space between document parts. When paragraphs are selected, add space between paragraphs. When sentences are
    selected, add space between sentences.

    Args:
        document_id: Document ID

    Request Body:
        {
            "spacing": {
                "paragraphs": false,
                "sentences": false
            },
        }

    Returns:
        JSON response with sacing result

    Example Response:
        {
            "success": true,
            "output_path": "/path/to/edited_document.docx",
            "format": "docx",
        }
    """
    logger.info(f"Spacing requested for document {document_id}")

    validate_document_id(document_id)

    # Validate request data
    data = request.get_json()
    if not data:
        raise ValidationException("Request body is required")

    if 'spacing' not in data:
        raise ValidationException("'spacing' field is required in request body")

    validated_data = validate_schema(SpacingOptionsSchema, data['spacing'])

    # Apply framing
    document_service = get_document_service()
    output_folder = current_app.config['OUTPUT_FOLDER']

    result = document_service.apply_spacing(
        document_id=document_id,
        spacing_options=validated_data.dict(),
        output_folder=output_folder
    )

    return jsonify(result), 200

@documents_bp.route('/documents/<document_id>/keywords', methods=['PUT'])
def add_keywords(document_id: str):
    """
    Extract keywords from document sections and add them as initial paragraphs after headings.

    For each section (identified by Heading 2, 3, etc.), this endpoint:
    1. Extracts the most relevant nouns using spaCy NLP (Italian language model)
    2. Adds a paragraph with the keywords right after the section heading
    3. Formats the keywords in italic style

    Args:
        document_id: Document ID

    Request Body:
        {
            "keywords": {
                "max_keywords": 5,
                "include_proper_nouns": true
            }
        }

    Returns:
        JSON response with keyword extraction result

    Example Response:
        {
            "success": true,
            "output_path": "/path/to/keywords_document.docx",
            "format": "docx",
            "sections_processed": 10,
            "total_keywords": 45,
            "keyword_options": {...}
        }
    """
    logger.info(f"Keyword extraction requested for document {document_id}")

    validate_document_id(document_id)

    # Validate request data
    data = request.get_json()
    if not data:
        raise ValidationException("Request body is required")

    if 'keywords' not in data:
        raise ValidationException("'keywords' field is required in request body")

    validated_data = validate_schema(KeywordOptionsSchema, data['keywords'])

    # Apply keyword extraction
    document_service = get_document_service()
    output_folder = current_app.config['OUTPUT_FOLDER']

    result = document_service.apply_keywords(
        document_id=document_id,
        keyword_options=validated_data.dict(),
        output_folder=output_folder
    )

    return jsonify(result), 200

@documents_bp.route('/documents/<document_id>/styles', methods=['GET'])
def get_document_styles(document_id: str):
    """
    Get available formatting styles for document.

    Args:
        document_id: Document ID

    Returns:
        JSON response with available styles
    """
    logger.info(f"Style info requested for document {document_id}")

    validate_document_id(document_id)

    document_service = get_document_service()
    document = document_service.get_document(document_id)

    formatting_service = get_formatting_service()
    styles = formatting_service.get_available_styles(document['file_extension'])

    return jsonify(styles), 200


@documents_bp.route('/documents/<document_id>/summarize', methods=['POST'])
@limiter.limit("10 per minute")
def summarize_document(document_id: str):
    """
    Generate summary of document using Ollama.

    Args:
        document_id: Document ID

    Request Body:
        {
            "summary_type": "brief"  # brief, detailed, executive
        }

    Returns:
        JSON response with summary

    Example Response:
        {
            "document_id": "uuid",
            "document_name": "document.pdf",
            "summary": "This document discusses...",
            "key_points": ["Point 1", "Point 2"],
            "summary_type": "brief",
            "original_length": 5000,
            "summary_length": 200,
            "compression_ratio": 0.04
        }
    """
    logger.info(f"Summarization requested for document {document_id}")

    validate_document_id(document_id)

    # Validate request data
    data = request.get_json() or {}
    validated_data = validate_schema(SummarizeRequestSchema, data)

    # Generate summary
    document_service = get_document_service()
    result = document_service.summarize_document(
        document_id=document_id,
        summary_type=validated_data.summary_type
    )

    return jsonify(result), 200


@documents_bp.route('/documents/<document_id>/paraphrase', methods=['POST'])
@limiter.limit("10 per minute")
def paraphrase_document(document_id: str):
    """
    Paraphrase document using Ollama.

    Args:
        document_id: Document ID

    Request Body:
        {
            "style": "formal",  # formal, casual, professional, simple
            "sections": [0, 1, 2]  # Optional: specific sections to paraphrase
        }

    Returns:
        JSON response with paraphrased content

    Example Response:
        {
            "document_id": "uuid",
            "document_name": "document.pdf",
            "style": "formal",
            "total_sections": 5,
            "paraphrased_sections": {
                "0": "Paraphrased text...",
                "1": "Paraphrased text..."
            }
        }
    """
    logger.info(f"Paraphrasing requested for document {document_id}")

    validate_document_id(document_id)

    # Validate request data
    data = request.get_json() or {}
    validated_data = validate_schema(ParaphraseRequestSchema, data)

    # Paraphrase document
    document_service = get_document_service()
    result = document_service.paraphrase_document(
        document_id=document_id,
        style=validated_data.style,
        sections=validated_data.sections
    )

    return jsonify(result), 200


@documents_bp.route('/text/summarize', methods=['POST'])
@limiter.limit("10 per minute")
def summarize_text():
    """
    Summarize text directly (without uploading document).

    Request Body:
        {
            "text": "Long text to summarize...",
            "max_length": 500
        }

    Returns:
        JSON response with summary
    """
    logger.info("Direct text summarization requested")

    # Validate request data
    data = request.get_json()
    if not data:
        raise ValidationException("Request body is required")

    validated_data = validate_schema(TextSummarizeRequestSchema, data)

    # Summarize text
    ollama_service = get_ollama_service()
    summary = ollama_service.summarize_text(
        text=validated_data.text,
        max_length=validated_data.max_length
    )

    return jsonify({
        'summary': summary,
        'original_length': len(validated_data.text),
        'summary_length': len(summary)
    }), 200


@documents_bp.route('/text/paraphrase', methods=['POST'])
@limiter.limit("10 per minute")
def paraphrase_text():
    """
    Paraphrase text directly (without uploading document).

    Request Body:
        {
            "text": "Text to paraphrase...",
            "style": "formal"
        }

    Returns:
        JSON response with paraphrased text
    """
    logger.info("Direct text paraphrasing requested")

    # Validate request data
    data = request.get_json()
    if not data:
        raise ValidationException("Request body is required")

    validated_data = validate_schema(TextParaphraseRequestSchema, data)

    # Paraphrase text
    ollama_service = get_ollama_service()
    paraphrased = ollama_service.paraphrase_text(
        text=validated_data.text,
        style=validated_data.style
    )

    return jsonify({
        'paraphrased_text': paraphrased,
        'style': validated_data.style,
        'original_length': len(validated_data.text),
        'paraphrased_length': len(paraphrased)
    }), 200


@documents_bp.route('/documents/<document_id>/download', methods=['GET'])
def download_document(document_id: str):
    """
    Download formatted document.

    Args:
        document_id: Document ID

    Returns:
        File download
    """
    logger.info(f"Download requested for document {document_id}")

    validate_document_id(document_id)

    document_service = get_document_service()
    document = document_service.get_document(document_id)

    # Determine which file to send
    file_path = document.get('formatted_path') or document['file_path']

    return send_file(
        file_path,
        as_attachment=True,
        download_name=document['original_filename']
    )


@documents_bp.route('/documents/<document_id>/preview', methods=['GET'])
def preview_document(document_id: str):
    """
    Get document preview (metadata and text excerpt).

    Args:
        document_id: Document ID

    Returns:
        JSON response with preview
    """
    logger.info(f"Preview requested for document {document_id}")

    validate_document_id(document_id)

    document_service = get_document_service()
    document = document_service.get_document(document_id)

    # Extract text if not already done
    if not document.get('text_content'):
        document_service.extract_text(document_id)
        document = document_service.get_document(document_id)

    from app.utils.text_extractor import get_text_preview
    preview = get_text_preview(document['text_content'], length=300)

    return jsonify({
        'document_id': document['id'],
        'original_filename': document['original_filename'],
        'file_size': document['file_size'],
        'file_extension': document['file_extension'],
        'text_preview': preview,
        'character_count': len(document['text_content']),
        'word_count': len(document['text_content'].split())
    }), 200
