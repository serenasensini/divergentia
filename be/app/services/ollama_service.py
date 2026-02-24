"""
Ollama Service - AI-powered text processing (Summarization & Paraphrasing)
"""
import logging
import time
from typing import Dict, List, Optional, Any
from functools import wraps

import ollama
from flask import current_app

from app.exceptions.custom_exceptions import (
    OllamaConnectionException,
    OllamaProcessingException
)

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on failure.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise
                    logger.warning(
                        f"Attempt {retries} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


class OllamaService:
    """Service for interacting with Ollama local models for text processing"""

    def __init__(self):
        """Initialize Ollama service with configuration from Flask app"""
        self.base_url = current_app.config.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.model = current_app.config.get('OLLAMA_MODEL', 'llama2')
        self.timeout = current_app.config.get('OLLAMA_TIMEOUT', 120)
        self.max_retries = current_app.config.get('OLLAMA_MAX_RETRIES', 3)

        # Cache for repeated requests (simple in-memory cache)
        self._cache: Dict[str, Any] = {}

        logger.info(f"Ollama service initialized with model: {self.model}")

    def _get_cache_key(self, operation: str, text: str, **kwargs) -> str:
        """Generate cache key for request"""
        params_str = '_'.join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{operation}_{hash(text)}_{params_str}"

    @retry_on_failure(max_retries=3, delay=2.0)
    def _generate_completion(
        self,
        prompt: str,
        stream: bool = False,
        **options
    ) -> str:
        """
        Generate completion from Ollama model.

        Args:
            prompt: Input prompt for the model
            stream: Whether to stream the response
            **options: Additional options for the model

        Returns:
            Generated text response

        Raises:
            OllamaConnectionException: If connection to Ollama fails
            OllamaProcessingException: If processing fails
        """
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                stream=stream,
                **options
            )

            if stream:
                # Handle streaming response
                full_response = ""
                for chunk in response:
                    full_response += chunk.get('response', '')
                return full_response
            else:
                return response.get('response', '')

        except ConnectionError as e:
            logger.error(f"Failed to connect to Ollama: {str(e)}")
            raise OllamaConnectionException(f"Connection failed: {str(e)}")
        except Exception as e:
            logger.error(f"Ollama processing error: {str(e)}")
            raise OllamaProcessingException(f"Processing failed: {str(e)}")

    def summarize_text(
        self,
        text: str,
        max_length: int = 500,
        use_cache: bool = True
    ) -> str:
        """
        Summarize the given text using Ollama.

        Args:
            text: Text to summarize
            max_length: Maximum length of summary in words
            use_cache: Whether to use cached results

        Returns:
            Summarized text
        """
        logger.info(f"Summarizing text (length: {len(text)} chars)")

        # Check cache
        cache_key = self._get_cache_key('summarize', text, max_length=max_length)
        if use_cache and cache_key in self._cache:
            logger.info("Returning cached summary")
            return self._cache[cache_key]

        prompt = f"""Please provide a concise summary of the following text.
The summary should be approximately {max_length} words or less, capturing the main points and key information.

Text to summarize:
{text}

Summary:"""

        summary = self._generate_completion(prompt)

        # Cache result
        if use_cache:
            self._cache[cache_key] = summary

        logger.info("Text summarization completed")
        return summary.strip()

    def paraphrase_text(
        self,
        text: str,
        style: str = 'formal',
        use_cache: bool = True
    ) -> str:
        """
        Paraphrase the given text using Ollama.

        Args:
            text: Text to paraphrase
            style: Style of paraphrasing ('formal', 'casual', 'professional', 'simple')
            use_cache: Whether to use cached results

        Returns:
            Paraphrased text
        """
        logger.info(f"Paraphrasing text with style: {style}")

        # Check cache
        cache_key = self._get_cache_key('paraphrase', text, style=style)
        if use_cache and cache_key in self._cache:
            logger.info("Returning cached paraphrase")
            return self._cache[cache_key]

        style_instructions = {
            'formal': 'in a formal and professional tone',
            'casual': 'in a casual and conversational tone',
            'professional': 'in a professional business tone',
            'simple': 'in simple and easy-to-understand language'
        }

        style_instruction = style_instructions.get(style.lower(), style_instructions['formal'])

        prompt = f"""Please paraphrase the following text {style_instruction}.
Maintain the original meaning while using different words and sentence structures.

Original text:
{text}

Paraphrased text:"""

        paraphrased = self._generate_completion(prompt)

        # Cache result
        if use_cache:
            self._cache[cache_key] = paraphrased

        logger.info("Text paraphrasing completed")
        return paraphrased.strip()

    def summarize_document(
        self,
        text: str,
        summary_type: str = 'brief'
    ) -> Dict[str, Any]:
        """
        Summarize an entire document with metadata.

        Args:
            text: Full document text
            summary_type: Type of summary ('brief', 'detailed', 'executive')

        Returns:
            Dictionary with summary and metadata
        """
        logger.info(f"Summarizing document (type: {summary_type})")

        # Determine max length based on summary type
        length_map = {
            'brief': 200,
            'detailed': 800,
            'executive': 400
        }
        max_length = length_map.get(summary_type, 500)

        # Generate summary
        summary = self.summarize_text(text, max_length=max_length)

        # Extract key points
        key_points = self.get_key_points(text, num_points=5)

        return {
            'summary': summary,
            'key_points': key_points,
            'summary_type': summary_type,
            'original_length': len(text),
            'summary_length': len(summary),
            'compression_ratio': round(len(summary) / len(text), 2)
        }

    def batch_paraphrase(
        self,
        text_chunks: List[str],
        style: str = 'formal'
    ) -> List[str]:
        """
        Paraphrase multiple text chunks.

        Args:
            text_chunks: List of text chunks to paraphrase
            style: Style of paraphrasing

        Returns:
            List of paraphrased texts
        """
        logger.info(f"Batch paraphrasing {len(text_chunks)} chunks")

        paraphrased_chunks = []
        for i, chunk in enumerate(text_chunks):
            logger.debug(f"Paraphrasing chunk {i+1}/{len(text_chunks)}")
            paraphrased = self.paraphrase_text(chunk, style=style)
            paraphrased_chunks.append(paraphrased)

        logger.info("Batch paraphrasing completed")
        return paraphrased_chunks

    def get_key_points(
        self,
        text: str,
        num_points: int = 5
    ) -> List[str]:
        """
        Extract key points from text.

        Args:
            text: Text to analyze
            num_points: Number of key points to extract

        Returns:
            List of key points
        """
        logger.info(f"Extracting {num_points} key points from text")

        prompt = f"""Please extract the {num_points} most important key points from the following text.
Present each point as a clear, concise bullet point.

Text:
{text}

Key points (one per line, numbered):"""

        response = self._generate_completion(prompt)

        # Parse response into list
        lines = response.strip().split('\n')
        key_points = []
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering/bullet points
                clean_line = line.lstrip('0123456789.-•) ').strip()
                if clean_line:
                    key_points.append(clean_line)

        logger.info(f"Extracted {len(key_points)} key points")
        return key_points[:num_points]

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 2000,
        overlap: int = 200
    ) -> List[str]:
        """
        Split large text into manageable chunks for processing.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks in characters

        Returns:
            List of text chunks
        """
        logger.info(f"Chunking text (size: {len(text)} chars)")

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending
                sentence_ends = ['. ', '! ', '? ', '\n\n']
                best_break = end
                for ending in sentence_ends:
                    pos = text.rfind(ending, start, end)
                    if pos > start:
                        best_break = pos + len(ending)
                        break
                end = best_break

            chunks.append(text[start:end].strip())
            start = end - overlap

        logger.info(f"Created {len(chunks)} chunks")
        return chunks

    def clear_cache(self) -> None:
        """Clear the request cache"""
        logger.info("Clearing Ollama service cache")
        self._cache.clear()

    def health_check(self) -> Dict[str, Any]:
        """
        Check if Ollama service is available.

        Returns:
            Dictionary with health status
        """
        try:
            # Try a simple generation
            response = self._generate_completion("Hello", stream=False)
            return {
                'status': 'healthy',
                'model': self.model,
                'base_url': self.base_url,
                'available': True
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'model': self.model,
                'base_url': self.base_url,
                'available': False,
                'error': str(e)
            }


# Singleton instance
_ollama_service_instance: Optional[OllamaService] = None


def get_ollama_service() -> OllamaService:
    """
    Get or create OllamaService singleton instance.

    Returns:
        OllamaService instance (singleton)
    """
    global _ollama_service_instance

    if _ollama_service_instance is None:
        _ollama_service_instance = OllamaService()
        logger.info("Ollama service singleton instance created")

    return _ollama_service_instance
