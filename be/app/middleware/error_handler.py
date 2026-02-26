"""
Error Handler Middleware
"""
import logging
from flask import jsonify
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
