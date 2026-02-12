"""
Security Headers Middleware
"""
import logging
from flask import Response

logger = logging.getLogger(__name__)


def setup_security_headers(response: Response) -> Response:
    """
    Add security headers to response.

    Args:
        response: Flask response object

    Returns:
        Response with security headers
    """
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'

    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # XSS Protection (for older browsers)
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # Content Security Policy (adjust as needed)
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline';"
    )

    # Permissions Policy (formerly Feature-Policy)
    response.headers['Permissions-Policy'] = (
        "geolocation=(), microphone=(), camera=()"
    )

    return response
