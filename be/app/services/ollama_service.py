"""
Ollama Service - AI-powered text processing (Summarization & Paraphrasing)
"""
import logging
import re
import time
from contextlib import contextmanager
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
        # `default_model` is the server-configured fallback (see issue #22):
        # when a caller requests a specific model (e.g. an FE "AI model tier")
        # that turns out to be unavailable on this Ollama instance, we degrade
        # gracefully to this default instead of failing the whole request.
        self.default_model = current_app.config.get('OLLAMA_MODEL', 'llama3:8b')
        self.model = self.default_model
        self.timeout = current_app.config.get('OLLAMA_TIMEOUT', 120)
        self.max_retries = current_app.config.get('OLLAMA_MAX_RETRIES', 3)

        # Explicit client bound to the configured base URL so requests are not
        # sent to the library default host (127.0.0.1:11434).
        self._client = ollama.Client(host=self.base_url)

        # Cache for repeated requests (simple in-memory cache)
        self._cache: Dict[str, Any] = {}

        logger.info(f"Ollama service initialized with model: {self.model} at {self.base_url}")

    def _get_cache_key(self, operation: str, text: str, **kwargs) -> str:
        """Generate cache key for request"""
        params_str = '_'.join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{operation}_{hash(text)}_{params_str}"

    @contextmanager
    def _use_model(self, model: Optional[str]):
        """
        Temporarily use ``model`` for the Ollama calls made within this
        context, restoring the configured default model afterwards.

        This lets a single request (e.g. one summarize/paraphrase/keyword
        call) opt into a specific model — such as one of the FE's "AI model
        tier" reference models (see issue #22) — without mutating shared
        service state beyond the current call. A falsy ``model`` is a no-op:
        the service keeps using its configured default.

        Args:
            model: Ollama model tag to use for this call, or None/'' to keep
                the current default.
        """
        if not model:
            yield
            return
        original_model = self.model
        self.model = model
        try:
            yield
        finally:
            self.model = original_model

    # Human readable names (in English) for the most common ISO 639-1 codes.
    # Passing an explicit language name to the model yields more reliable
    # results than only asking it to "keep the original language".
    _LANGUAGE_NAMES: Dict[str, str] = {
        'it': 'Italian',
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'pt': 'Portuguese',
        'nl': 'Dutch',
        'ca': 'Catalan',
        'ro': 'Romanian',
    }

    def _detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of ``text`` and return its ISO 639-1 code.

        Uses the ``langdetect`` library. Returns ``None`` when the text is empty
        or detection fails, so callers can gracefully fall back to a generic
        "keep the original language" instruction.

        Args:
            text: Text to analyse

        Returns:
            ISO 639-1 language code (e.g. "it", "en") or ``None``.
        """
        if not text or not text.strip():
            return None

        try:
            from langdetect import detect, DetectorFactory
            # Make detection deterministic across runs.
            DetectorFactory.seed = 0
            language = detect(text)
            logger.debug(f"Detected document language for summarization: '{language}'")
            return language
        except Exception as e:
            logger.warning(f"Language detection failed ({str(e)}); summary language left generic")
            return None

    def _language_instruction(self, text: str) -> str:
        """
        Build a prompt instruction forcing the output language to match ``text``.

        When the language can be detected and mapped to a known name the model
        is told explicitly (e.g. "Write the summary in Italian."). Otherwise a
        generic instruction to preserve the original language is used.
        """
        language = self._detect_language(text)
        language_name = self._LANGUAGE_NAMES.get(language or '', None)
        if language_name:
            return (
                f"Write the summary in {language_name}, the same language as the "
                f"original text. Do not translate the content into any other language."
            )
        return (
            "Write the summary in the same language as the original text. "
            "Do not translate the content into any other language."
        )

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
            response = self._client.generate(
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
            # Graceful degradation (issue #22): if a non-default model (e.g.
            # an FE "AI model tier" the operator hasn't pulled) fails, retry
            # once with the server-configured default model instead of
            # failing the whole request outright.
            if self.model != self.default_model:
                logger.warning(
                    f"Model '{self.model}' unavailable or failed; "
                    f"falling back to default model '{self.default_model}'"
                )
                try:
                    response = self._client.generate(
                        model=self.default_model,
                        prompt=prompt,
                        stream=stream,
                        **options
                    )
                    if stream:
                        full_response = ""
                        for chunk in response:
                            full_response += chunk.get('response', '')
                        return full_response
                    return response.get('response', '')
                except Exception as fallback_error:
                    logger.error(f"Ollama processing error (fallback model): {str(fallback_error)}")
                    raise OllamaProcessingException(f"Processing failed: {str(fallback_error)}")

            logger.error(f"Ollama processing error: {str(e)}")
            raise OllamaProcessingException(f"Processing failed: {str(e)}")

    def summarize_text(
        self,
        text: str,
        max_length: int = 500,
        model: Optional[str] = None,
        use_cache: bool = True
    ) -> str:
        """
        Summarize the given text using Ollama.

        Args:
            text: Text to summarize
            max_length: Maximum length of summary in words
            model: Optional Ollama model tag to use for this call (e.g. one of
                the FE "AI model tier" reference models). Falls back to the
                service's configured default model when omitted.
            use_cache: Whether to use cached results

        Returns:
            Summarized text
        """
        logger.info(f"Summarizing text (length: {len(text)} chars)")

        # Check cache
        cache_key = self._get_cache_key('summarize', text, max_length=max_length, model=model or self.model)
        if use_cache and cache_key in self._cache:
            logger.info("Returning cached summary")
            return self._cache[cache_key]

        prompt = f"""Please provide a concise summary of the following text.
The summary should be approximately {max_length} words or less, capturing the main points and key information.
{self._language_instruction(text)}

Text to summarize:
{text}

Summary:"""

        with self._use_model(model):
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
        model: Optional[str] = None,
        use_cache: bool = True
    ) -> str:
        """
        Paraphrase the given text using Ollama.

        Args:
            text: Text to paraphrase
            style: Style of paraphrasing ('formal', 'casual', 'professional', 'simple')
            model: Optional Ollama model tag to use for this call (e.g. one of
                the FE "AI model tier" reference models). Falls back to the
                service's configured default model when omitted.
            use_cache: Whether to use cached results

        Returns:
            Paraphrased text
        """
        logger.info(f"Paraphrasing text with style: {style}")

        # Check cache
        cache_key = self._get_cache_key('paraphrase', text, style=style, model=model or self.model)
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
{self._language_instruction(text)}

Original text:
{text}

Paraphrased text:"""

        with self._use_model(model):
            paraphrased = self._generate_completion(prompt)

        # Cache result
        if use_cache:
            self._cache[cache_key] = paraphrased

        logger.info("Text paraphrasing completed")
        return paraphrased.strip()

    def summarize_document(
        self,
        text: str,
        summary_type: str = 'brief',
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Summarize an entire document with metadata.

        Args:
            text: Full document text
            summary_type: Type of summary ('brief', 'detailed', 'executive')
            model: Optional Ollama model tag to use (see issue #22 AI model tiers).

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
        summary = self.summarize_text(text, max_length=max_length, model=model)

        # Extract key points
        key_points = self.get_key_points(text, num_points=5, model=model)

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
        style: str = 'formal',
        model: Optional[str] = None
    ) -> List[str]:
        """
        Paraphrase multiple text chunks.

        Args:
            text_chunks: List of text chunks to paraphrase
            style: Style of paraphrasing
            model: Optional Ollama model tag to use (see issue #22 AI model tiers).

        Returns:
            List of paraphrased texts
        """
        logger.info(f"Batch paraphrasing {len(text_chunks)} chunks")

        paraphrased_chunks = []
        for i, chunk in enumerate(text_chunks):
            logger.debug(f"Paraphrasing chunk {i+1}/{len(text_chunks)}")
            paraphrased = self.paraphrase_text(chunk, style=style, model=model)
            paraphrased_chunks.append(paraphrased)

        logger.info("Batch paraphrasing completed")
        return paraphrased_chunks

    def extract_keywords(
        self,
        text: str,
        max_keywords: int = 5,
        model: Optional[str] = None,
        use_cache: bool = True
    ) -> List[str]:
        """
        Estrae le parole chiave più rilevanti da un testo utilizzando un modello Ollama.

        Questa funzione invia un prompt in italiano al modello Ollama per identificare
        le parole chiave più significative nel contesto del testo fornito. Il modello
        analizza il contenuto semantico e restituisce una lista di parole chiave ordinate
        per rilevanza.

        Funzionalità:
        - Utilizza un prompt ottimizzato in italiano
        - Supporta la selezione di modelli specifici (es. llama2, mistral, phi)
        - Implementa caching per migliorare le performance su richieste ripetute
        - Effettua pulizia automatica della risposta (rimozione numerazione, conversione lowercase)
        - Gestisce diversi formati di risposta dal modello

        Flusso di esecuzione:
        1. Verifica cache per risultati precedenti
        2. Imposta il modello specificato (o usa quello di default)
        3. Genera prompt in italiano con il testo da analizzare
        4. Invia richiesta al modello Ollama
        5. Parse e pulizia della risposta (rimozione prefissi, numerazione)
        6. Conversione in lowercase e limitazione al numero richiesto
        7. Salvataggio in cache e restituzione risultati

        Args:
            text (str): Testo da cui estrarre le parole chiave
            max_keywords (int, optional): Numero massimo di parole chiave da estrarre (range: 1-10).
                                         Default: 5
            model (Optional[str], optional): Nome del modello Ollama specifico da utilizzare
                                            (es. 'llama2', 'mistral', 'phi').
                                            Se None, usa il modello configurato di default.
                                            Default: None
            use_cache (bool, optional): Se True, utilizza risultati in cache per richieste identiche.
                                       Se False, forza una nuova richiesta al modello.
                                       Default: True

        Returns:
            List[str]: Lista di parole chiave estratte in formato lowercase, ordinate per rilevanza.
                      La lista conterrà al massimo 'max_keywords' elementi.
                      Esempio: ['intelligenza', 'artificiale', 'apprendimento', 'dati', 'modello']

        Raises:
            OllamaConnectionException: Se la connessione al servizio Ollama fallisce
            OllamaProcessingException: Se si verifica un errore durante l'elaborazione

        Note:
            - Il prompt richiede al modello di rispondere SOLO con parole chiave separate da virgola
            - La funzione gestisce automaticamente risposte con formati diversi (numerazioni, prefissi)
            - Per testi molto lunghi (>2000 caratteri), considera di suddividerli in chunk
            - Il modello specificato deve essere già scaricato localmente (ollama pull <model>)
        """
        logger.info(f"Extracting {max_keywords} keywords from text using Ollama")

        # Check cache
        cache_key = self._get_cache_key('extract_keywords', text, max_keywords=max_keywords, model=model or self.model)
        if use_cache and cache_key in self._cache:
            logger.info("Returning cached keywords")
            return self._cache[cache_key]

        # Use specified model or default
        original_model = self.model
        if model:
            self.model = model
            logger.info(f"Using specific model for keyword extraction: {model}")

        try:
            prompt = f"""Estrai le {max_keywords} parole chiave più rilevanti da questo testo.
                    Rispondi SOLO con le parole chiave separate da virgola, senza numerazione o spiegazioni. Le parole chiave devono essere nella lingua originale
                    del testo riportato di seguito e rappresentare i concetti più importanti. Non includere stop words o parole comuni, ma solo termini significativi per il contenuto.
                    Non usare sinonimi della stessa parola, ma scegli la forma più rappresentativa. Se il testo è troppo lungo, concentrati sulle sezioni più rilevanti.
                    Usare per l'output solo la lingua originale del testo, senza traduzioni o adattamenti.
                    
                    Testo:
                    {text}
                    
                    Parole chiave:"""
            # NOTE: do not log `prompt`/`response` at any level: both embed
            # the source document's text, which may contain personal or
            # otherwise sensitive information (see issue #12).
            logger.debug(f"Prompt for keyword extraction built (length: {len(prompt)} chars)")
            response = self._generate_completion(prompt, stream=True)
            logger.debug(f"Raw response for keyword extraction received (length: {len(response)} chars)")

            # Parse response - expecting comma-separated keywords
            keywords_text = response.strip()

            # Remove common prefixes if present
            keywords_text = re.sub(r'^(parole chiave:|keywords:|risposta:)\s*', '', keywords_text, flags=re.IGNORECASE)

            # Split by comma and clean
            keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]

            # Additional cleaning - remove numbering if present
            cleaned_keywords = []
            for kw in keywords:
                # Remove leading numbers and dots
                clean_kw = re.sub(r'^\d+[.)]\s*', '', kw).strip()
                if clean_kw:
                    cleaned_keywords.append(clean_kw.lower())

            # Ensure we don't exceed max_keywords
            keywords = cleaned_keywords[:max_keywords]

            # Cache result
            if use_cache:
                self._cache[cache_key] = keywords

            logger.info(f"Extracted {len(keywords)} keywords")
            return keywords

        finally:
            # Restore original model
            if model:
                self.model = original_model

    def get_key_points(
        self,
        text: str,
        num_points: int = 5,
        model: Optional[str] = None
    ) -> List[str]:
        """
        Extract key points from text.

        Args:
            text: Text to analyze
            num_points: Number of key points to extract
            model: Optional Ollama model tag to use (see issue #22 AI model tiers).

        Returns:
            List of key points
        """
        logger.info(f"Extracting {num_points} key points from text")

        prompt = f"""Please extract the {num_points} most important key points from the following text.
                Present each point as a clear, concise bullet point. Use simple language and focus on the main ideas without unnecessary details.
                The output should be a list of key points, each on a new line, without numbering or additional formatting, with
                the same language as the input text and the same level of formality. Keywords shouldn't include stop words or common words, 
                but should be relevant to the main topics of the text and they shouldn't include synonyms of the same word. If the text is too long, 
                focus on the most relevant sections to extract key points.
                
                Text:
                {text}
                
                Key points (one per line, numbered):"""
        # NOTE: do not log `prompt`/`response` at any level: both embed the
        # source document's text, which may contain personal or otherwise
        # sensitive information (see issue #12).
        logger.debug(f"Prompt for key point extraction built (length: {len(prompt)} chars)")
        with self._use_model(model):
            response = self._generate_completion(prompt)
        logger.debug(f"Extracted {num_points} key points (response length: {len(response)} chars)")

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

        This is intentionally lightweight: it only verifies that the Ollama
        server is reachable and that the configured model is installed, using
        the models listing endpoint. It deliberately avoids running a real
        text generation, which would load the model into memory and make the
        (frequently polled) health endpoint slow.

        Returns:
            Dictionary with health status
        """
        try:
            # Lightweight availability probe: list installed models.
            listed = self._client.list()
            models = listed.get('models', []) if isinstance(listed, dict) else []

            def _model_name(entry: Any) -> str:
                if isinstance(entry, dict):
                    return entry.get('name') or entry.get('model') or ''
                # ollama client may return objects with a ``model`` attribute
                return getattr(entry, 'model', '') or getattr(entry, 'name', '')

            available_models = {_model_name(m) for m in models}
            # Match with or without an explicit ":latest" tag.
            model_present = (
                self.model in available_models
                or f"{self.model}:latest" in available_models
                or any(name.split(':', 1)[0] == self.model.split(':', 1)[0]
                       for name in available_models)
            )

            return {
                'status': 'healthy' if model_present else 'degraded',
                'model': self.model,
                'base_url': self.base_url,
                'available': model_present,
                'installed_models': sorted(available_models),
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
