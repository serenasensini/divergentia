"""
Flask Application Factory and Configuration
"""
import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

# Initialize extensions
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[]
)

cache = Cache()


def create_app(config_name: str = None) -> Flask:
    """
    Application factory pattern for creating Flask app instances.

    Args:
        config_name: Configuration name (development, production, testing)

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    from app.config import get_config
    app.config.from_object(get_config(config_name))

    # Initialize extensions
    initialize_extensions(app)

    # Setup logging
    setup_logging(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Register middleware
    register_middleware(app)

    return app


def initialize_extensions(app: Flask) -> None:
    """
    Initialize Flask extensions.

    Args:
        app: Flask application instance
    """
    # CORS configuration for Angular frontend
    CORS(app,
         origins=app.config['CORS_ORIGINS'],
         methods=app.config['CORS_METHODS'],
         allow_headers=app.config['CORS_ALLOW_HEADERS'],
         supports_credentials=True)

    # Rate limiter
    limiter.init_app(app)

    # Cache
    cache.init_app(app)


def setup_logging(app: Flask) -> None:
    """
    Configure application logging.

    Args:
        app: Flask application instance
    """
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))

    # Remove all existing handlers from app.logger to prevent duplicates
    app.logger.handlers.clear()

    # Create formatter
    console_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)

    # File handler (optional)
    file_handler = None
    if app.config.get('LOG_FILE'):
        file_handler = logging.FileHandler(app.config['LOG_FILE'])
        file_handler.setLevel(log_level)
        file_handler.setFormatter(console_formatter)
        app.logger.addHandler(file_handler)

    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)

    # Prevent propagation to avoid duplicate logs
    app.logger.propagate = False

    # Configure root logger for module loggers to prevent duplicates
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(log_level)
    if file_handler:
        root_logger.addHandler(file_handler)

    app.logger.info('Flask application initialized')


def register_blueprints(app: Flask) -> None:
    """
    Register application blueprints.

    Args:
        app: Flask application instance
    """
    from app.blueprints.documents.routes import documents_bp

    app.register_blueprint(documents_bp, url_prefix='/api')

    app.logger.info('Blueprints registered')


def register_error_handlers(app: Flask) -> None:
    """
    Register global error handlers.

    Args:
        app: Flask application instance
    """
    from app.middleware.error_handler import (
        handle_validation_error,
        handle_not_found,
        handle_internal_error,
        handle_custom_exception
    )
    from app.exceptions.custom_exceptions import ApplicationException

    app.register_error_handler(400, handle_validation_error)
    app.register_error_handler(404, handle_not_found)
    app.register_error_handler(500, handle_internal_error)
    app.register_error_handler(ApplicationException, handle_custom_exception)

    app.logger.info('Error handlers registered')


def register_middleware(app: Flask) -> None:
    """
    Register application middleware.

    Args:
        app: Flask application instance
    """
    from app.middleware.security import setup_security_headers

    app.after_request(setup_security_headers)

    app.logger.info('Middleware registered')
