"""
Unit tests for localised keyword labels and language detection.

These tests exercise ``detect_language`` and ``format_keywords`` without
loading the heavy spaCy model (the service instance is created via
``__new__`` so ``__init__``/model loading is skipped).
"""
import pytest

from app.services.keyword_service import KeywordService


@pytest.fixture
def service():
    svc = KeywordService.__new__(KeywordService)
    svc.nlp = None
    return svc


@pytest.mark.parametrize(
    "text, expected_lang",
    [
        ("Questo capitolo descrive i requisiti necessari per creare un blog aziendale.", "it"),
        ("This chapter describes the requirements needed to create a corporate blog.", "en"),
        ("Ce chapitre décrit les exigences nécessaires pour créer un blog interne.", "fr"),
        ("Este es un texto de ejemplo en idioma español con varias palabras.", "es"),
    ],
)
def test_detect_language(service, text, expected_lang):
    assert service.detect_language(text) == expected_lang


def test_detect_language_empty_uses_default(service):
    assert service.detect_language("   ") == service.DEFAULT_KEYWORD_LANGUAGE


def test_format_keywords_localised_prefix(service):
    kws = ["alpha", "beta", "gamma"]
    assert service.format_keywords(kws, language="it") == "Parole chiave: alpha, beta, gamma"
    assert service.format_keywords(kws, language="en") == "Keywords: alpha, beta, gamma"
    assert service.format_keywords(kws, language="fr") == "Mots-clés: alpha, beta, gamma"


def test_format_keywords_unknown_language_falls_back_to_english(service):
    assert service.format_keywords(["x"], language="zz") == "Keywords: x"


def test_format_keywords_default_language(service):
    assert service.format_keywords(["x"]) == "Keywords: x"


def test_format_keywords_empty_list(service):
    assert service.format_keywords([], language="it") == ""
