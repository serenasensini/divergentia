"""
Unit tests for Ollama Service
"""
import pytest
from unittest.mock import Mock, patch
from app.services.ollama_service import OllamaService


class TestOllamaService:
    """Test cases for OllamaService"""

    def test_summarize_text(self, app):
        """Test text summarization"""
        with app.app_context():
            service = OllamaService()

            with patch('ollama.generate') as mock_generate:
                mock_generate.return_value = {'response': 'This is a test summary.'}

                result = service.summarize_text("Long text to summarize", max_length=100)

                assert result == 'This is a test summary.'
                mock_generate.assert_called_once()

    def test_paraphrase_text(self, app):
        """Test text paraphrasing"""
        with app.app_context():
            service = OllamaService()

            with patch('ollama.generate') as mock_generate:
                mock_generate.return_value = {'response': 'Paraphrased text result.'}

                result = service.paraphrase_text("Original text", style='formal')

                assert result == 'Paraphrased text result.'
                mock_generate.assert_called_once()

    def test_chunk_text(self, app):
        """Test text chunking"""
        with app.app_context():
            service = OllamaService()

            long_text = "This is a test. " * 200
            chunks = service.chunk_text(long_text, chunk_size=100, overlap=20)

            assert len(chunks) > 1
            assert all(len(chunk) <= 120 for chunk in chunks)  # chunk_size + some buffer
