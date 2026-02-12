"""
Integration tests for Document API
"""
import pytest
import io
from pathlib import Path


class TestDocumentAPI:
    """Test cases for Document API endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'api_version' in data

    def test_supported_formats(self, client):
        """Test supported formats endpoint"""
        response = client.get('/api/formats/supported')

        assert response.status_code == 200
        data = response.get_json()
        assert 'supported_formats' in data
        assert 'format_details' in data

    def test_upload_document(self, client):
        """Test document upload"""
        # Create a test file
        data = {
            'file': (io.BytesIO(b'Test document content'), 'test.txt')
        }

        response = client.post(
            '/api/documents/upload',
            data=data,
            content_type='multipart/form-data'
        )

        assert response.status_code == 201
        data = response.get_json()
        assert 'document_id' in data
        assert data['original_filename'] == 'test.txt'

    def test_upload_invalid_file(self, client):
        """Test upload with invalid file type"""
        data = {
            'file': (io.BytesIO(b'Test content'), 'test.exe')
        }

        response = client.post(
            '/api/documents/upload',
            data=data,
            content_type='multipart/form-data'
        )

        assert response.status_code == 400

    def test_summarize_text_direct(self, client):
        """Test direct text summarization"""
        with pytest.skip("Requires Ollama to be running"):
            data = {
                'text': 'This is a long text that needs to be summarized.',
                'max_length': 100
            }

            response = client.post(
                '/api/text/summarize',
                json=data
            )

            assert response.status_code == 200
            result = response.get_json()
            assert 'summary' in result
