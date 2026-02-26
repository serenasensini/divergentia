"""
Keyword Extraction Service - Extract keywords from text using spaCy
"""
import logging
from typing import List, Set
from collections import Counter

logger = logging.getLogger(__name__)


class KeywordService:
    """Service for extracting keywords from text using spaCy NLP"""

    def __init__(self):
        """Initialize keyword service with Italian language model"""
        self.nlp = None
        self._load_model()

    def _load_model(self):
        """Load spaCy Italian language model"""
        try:
            import spacy
            try:
                self.nlp = spacy.load("it_core_news_lg-3.8.0")
                logger.info("Italian spaCy model loaded successfully")
            except OSError:
                logger.warning("Italian spaCy model not found. Attempting to download...")
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "spacy", "download", "it_core_news_lg-3.8.0"])
                self.nlp = spacy.load("it_core_news_lg-3.8.0")
                logger.info("Italian spaCy model downloaded and loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {str(e)}")
            raise Exception(f"Failed to initialize keyword service: {str(e)}")

    def extract_keywords(
        self,
        text: str,
        max_keywords: int = 5,
        include_proper_nouns: bool = True
    ) -> List[str]:
        """
        Extract keywords (nouns) from text using spaCy.

        Args:
            text: Text to analyze
            max_keywords: Maximum number of keywords to return
            include_proper_nouns: Whether to include proper nouns (names, places)

        Returns:
            List of extracted keywords sorted by frequency
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for keyword extraction")
            return []

        try:
            # Process text with spaCy
            doc = self.nlp(text)

            # Extract nouns and proper nouns
            nouns = []
            for token in doc:
                # Filter for nouns (NOUN) and optionally proper nouns (PROPN)
                if token.pos_ == "NOUN" or (include_proper_nouns and token.pos_ == "PROPN"):
                    # Skip stop words and very short words
                    if not token.is_stop and len(token.text) > 2:
                        # Use lemmatized form for better grouping
                        nouns.append(token.lemma_.lower())

            # Count frequency and get most common
            noun_counts = Counter(nouns)
            most_common = noun_counts.most_common(max_keywords)

            # Return only the words, not the counts
            keywords = [word for word, count in most_common]

            logger.debug(f"Extracted {len(keywords)} keywords from text of length {len(text)}")
            return keywords

        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []

    def format_keywords(self, keywords: List[str]) -> str:
        """
        Format keywords list into a readable string.

        Args:
            keywords: List of keywords

        Returns:
            Formatted string of keywords
        """
        if not keywords:
            return ""

        # Format as: "Parole chiave: keyword1, keyword2, keyword3"
        return f"Parole chiave: {', '.join(keywords)}"


# Singleton instance
_keyword_service_instance = None


def get_keyword_service() -> KeywordService:
    """
    Get singleton instance of keyword service.

    Returns:
        KeywordService instance
    """
    global _keyword_service_instance

    if _keyword_service_instance is None:
        _keyword_service_instance = KeywordService()

    return _keyword_service_instance

