"""
Test Configuration
"""
import pytest
import os
import tempfile
from app import create_app


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')

    # Create temporary directories for testing
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    app.config['OUTPUT_FOLDER'] = tempfile.mkdtemp()

    yield app

    # Cleanup
    import shutil
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        shutil.rmtree(app.config['UPLOAD_FOLDER'])
    if os.path.exists(app.config['OUTPUT_FOLDER']):
        shutil.rmtree(app.config['OUTPUT_FOLDER'])


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create CLI runner"""
    return app.test_cli_runner()
