"""
Error Handler Middleware
"""
import logging
from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException

from app.exceptions.custom_exceptions import ApplicationException

logger = logging.getLogger(__name__)


def handle_validation_error(error):
    """
    Handle 400 validation errors.

    Args:
        error: Error object

    Returns:
        JSON response with error details
    """
    logger.warning(f"Validation error: {str(error)}")

    response = {
        'error': 'ValidationError',
        'message': 'Invalid request data',
        'status_code': 400,
        'details': str(error)
    }

    return jsonify(response), 400


def handle_not_found(error):
    """
    Handle 404 not found errors.

    Args:
        error: Error object

    Returns:
        JSON response with error details
    """
    logger.warning(f"Resource not found: {str(error)}")

    response = {
        'error': 'NotFound',
        'message': 'The requested resource was not found',
        'status_code': 404
    }

    return jsonify(response), 404


def handle_internal_error(error):
    """
    Handle 500 internal server errors.

    Args:
        error: Error object

    Returns:
        JSON response with error details
    """
    logger.error(f"Internal server error: {str(error)}", exc_info=True)

    response = {
        'error': 'InternalServerError',
        'message': 'An internal server error occurred',
        'status_code': 500
    }

    return jsonify(response), 500


def handle_request_entity_too_large(error):
    """
    Handle 413 "Payload Too Large" errors.

    Raised automatically by Werkzeug when the incoming request body exceeds
    ``MAX_CONTENT_LENGTH`` (see ``app/config.py``), *before* the request body
    is fully read into memory. Without this handler Flask would fall back to
    the default HTML error page instead of a clear, actionable JSON response.

    Args:
        error: The RequestEntityTooLarge exception instance.

    Returns:
        JSON response including the configured maximum upload size.
    """
    max_size = current_app.config.get('MAX_CONTENT_LENGTH') or current_app.config.get('MAX_UPLOAD_SIZE', 0)
    max_size_mb = max_size / (1024 * 1024) if max_size else None

    logger.warning(f"Upload rejected: request exceeds the {max_size_mb:.1f}MB limit" if max_size_mb else "Upload rejected: request too large")

    response = {
        'error': 'FileTooLarge',
        'message': (
            f"File exceeds the maximum allowed size of {max_size_mb:.1f}MB"
            if max_size_mb else "File exceeds the maximum allowed size"
        ),
        'status_code': 413,
        'max_upload_size_bytes': max_size,
        'max_upload_size_mb': round(max_size_mb, 1) if max_size_mb else None,
    }

    return jsonify(response), 413


def handle_custom_exception(error: ApplicationException):
    """
    Handle custom application exceptions.

    Args:
        error: ApplicationException instance

    Returns:
        JSON response with error details
    """
    logger.error(f"Application exception: {error.message}")

    response = error.to_dict()

    return jsonify(response), error.status_code


def handle_http_exception(error: HTTPException):
    """
    Handle werkzeug HTTP exceptions.

    Args:
        error: HTTPException instance

    Returns:
        JSON response with error details
    """
    logger.warning(f"HTTP exception: {error.code} - {error.description}")

    response = {
        'error': error.name,
        'message': error.description,
        'status_code': error.code
    }

    return jsonify(response), error.code
