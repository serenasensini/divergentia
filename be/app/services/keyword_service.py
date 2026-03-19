"""
Keyword Extraction Service - Extract keywords from text using spaCy
"""
import logging
from typing import List, Dict, Optional, Any
from collections import Counter

from app.constants import (
    POS_NOUNS, POS_VERBS, POS_ADJECTIVES, POS_ADVERBS,
    MIN_KEYWORD_LENGTH
)

logger = logging.getLogger(__name__)


class KeywordService:
    """Service for extracting keywords from text using spaCy NLP"""

    def __init__(self) -> None:
        """Initialize keyword service with Italian language model"""
        self.nlp: Optional[Any] = None
        self._load_model()

    def _load_model(self) -> None:
        """Load spaCy Italian language model"""
        try:
            import spacy
            try:
                self.nlp = spacy.load("it_core_news_lg")
                logger.info("Italian spaCy model loaded successfully")
            except OSError:
                logger.warning("Italian spaCy model not found. Attempting to download...")
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "spacy", "download", "it_core_news_lg-3.8.0"])
                self.nlp = spacy.load("it_core_news_lg-3.8.0")
                logger.info("Italian spaCy model downloaded and loaded successfully")

            # Add sentencizer if not already in pipeline
            if "sentencizer" not in self.nlp.pipe_names:
                self.nlp.add_pipe("sentencizer")
                logger.info("Sentencizer added to spaCy pipeline")

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
                    if not token.is_stop and len(token.text) > MIN_KEYWORD_LENGTH:
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

    def analyze_pos(self, text: str) -> List[Dict[str, str]]:
        """
        Analyze text and return part-of-speech information for each token.

        Args:
            text: Text to analyze

        Returns:
            List of dictionaries with token information (text, pos, lemma, start_char, end_char)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for POS analysis")
            return []

        try:
            doc = self.nlp(text)
            tokens = []
            for token in doc:
                tokens.append({
                    'text': token.text,
                    'pos': token.pos_,
                    'lemma': token.lemma_,
                    'is_stop': token.is_stop,
                    'is_punct': token.is_punct,
                    'is_space': token.is_space,
                    'start_char': token.idx,
                    'end_char': token.idx + len(token.text)
                })
            return tokens
        except Exception as e:
            logger.error(f"Error analyzing POS: {str(e)}")
            return []

    def _check_pos(self, word: str, pos_types: List[str], pos_name: str = "POS") -> bool:
        """
        Generic part-of-speech checker.

        Args:
            word: Word to check
            pos_types: List of POS tags to check against (e.g., ["NOUN", "PROPN"])
            pos_name: Name of the POS for error logging (e.g., "noun", "verb")

        Returns:
            True if word matches any of the specified POS types, False otherwise
        """
        if not word or not word.strip():
            return False

        try:
            doc = self.nlp(word.strip())
            for token in doc:
                if not token.is_punct and not token.is_space:
                    return token.pos_ in pos_types
            return False
        except Exception as e:
            logger.error(f"Error checking if word is {pos_name}: {str(e)}")
            return False

    def is_noun(self, word: str) -> bool:
        """
        Check if a word is a noun.

        Args:
            word: Word to check

        Returns:
            True if word is a noun, False otherwise
        """
        return self._check_pos(word, POS_NOUNS, "noun")

    def is_verb(self, word: str) -> bool:
        """
        Check if a word is a verb.

        Args:
            word: Word to check

        Returns:
            True if word is a verb, False otherwise
        """
        return self._check_pos(word, POS_VERBS, "verb")

    def is_adjective(self, word: str) -> bool:
        """
        Check if a word is an adjective.

        Args:
            word: Word to check

        Returns:
            True if word is an adjective, False otherwise
        """
        return self._check_pos(word, POS_ADJECTIVES, "adjective")

    def is_adverb(self, word: str) -> bool:
        """
        Check if a word is an adverb.

        Args:
            word: Word to check

        Returns:
            True if word is an adverb, False otherwise
        """
        return self._check_pos(word, POS_ADVERBS, "adverb")

    def split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using spaCy's Sentencizer.

        This is more accurate than regex-based splitting as it:
        - Handles abbreviations correctly (e.g., "Dr.", "etc.")
        - Recognizes sentence boundaries in complex punctuation
        - Works with multiple languages
        - Handles edge cases like quotes and parentheses

        Args:
            text: Text to split into sentences

        Returns:
            List of sentences as strings
        """
        if not text or not text.strip():
            logger.debug("Empty text provided for sentence splitting")
            return []

        try:
            # Process text with spaCy (including sentencizer)
            doc = self.nlp(text)

            # Extract sentences
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

            logger.debug(f"Split text into {len(sentences)} sentences")
            return sentences

        except Exception as e:
            logger.error(f"Error splitting sentences: {str(e)}")
            # Fallback to simple regex split if spaCy fails
            logger.warning("Falling back to regex-based sentence splitting")
            import re
            sentences = re.split(r'(?<=[.!?])\s+', text)
            return [s.strip() for s in sentences if s.strip()]


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

