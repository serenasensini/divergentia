"""
Unit tests for table-based framing (sections / paragraphs / sentences).
"""
import os
import re
import tempfile

import pytest
from docx import Document
from docx.oxml.ns import qn

import app.services.keyword_service as ks
from app.services.formatting_service import get_formatting_service


class _FakeKeywordService:
    """Lightweight sentence splitter so tests don't need the spaCy model."""

    def split_sentences(self, text):
        return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text.strip()) if s.strip()]


@pytest.fixture
def stub_sentences(monkeypatch):
    monkeypatch.setattr(ks, "_keyword_service_instance", _FakeKeywordService())
    yield


def _build_doc(path):
    doc = Document()
    doc.add_paragraph("Chapter One", style="Heading 1")
    doc.add_paragraph("First body paragraph of the section.")
    doc.add_paragraph("A standalone paragraph. It has two sentences here.")
    doc.save(path)


def _frame(opts):
    with tempfile.TemporaryDirectory() as d:
        inp = os.path.join(d, "in.docx")
        out = os.path.join(d, "out.docx")
        _build_doc(inp)
        res = get_formatting_service().apply_framing(inp, out, {**opts, "use_tables": True})
        assert res["success"] is True
        return Document(out)


def _body_elements(doc):
    return list(doc.element.body)


def _has_adjacent_tables(doc):
    body = _body_elements(doc)
    return any(
        body[i].tag == qn('w:tbl') and body[i + 1].tag == qn('w:tbl')
        for i in range(len(body) - 1)
    )


def _top_border(table):
    b = table._element.find(qn('w:tblPr')).find(qn('w:tblBorders')).find(qn('w:top'))
    return b.get(qn('w:val')), b.get(qn('w:sz'))


class TestFraming:
    def test_sections_merge_into_single_table(self):
        doc = _frame({"sections": True})
        assert len(doc.tables) == 1
        cell = doc.tables[0].rows[0].cells[0]
        # Both body paragraphs of the section end up in the one cell.
        assert len(cell.paragraphs) == 2
        assert _top_border(doc.tables[0]) == ("double", "16")
        assert not _has_adjacent_tables(doc)

    def test_paragraphs_one_table_each(self):
        doc = _frame({"paragraphs": True})
        assert len(doc.tables) == 2
        for t in doc.tables:
            assert len(t.rows[0].cells[0].paragraphs) == 1
            assert _top_border(t) == ("single", "8")
        assert not _has_adjacent_tables(doc)

    def test_sentences_one_table_each(self, stub_sentences):
        doc = _frame({"sentences": True})
        # 1 sentence + 2 sentences = 3 tables.
        assert len(doc.tables) == 3
        texts = [t.rows[0].cells[0].text for t in doc.tables]
        assert texts == [
            "First body paragraph of the section.",
            "A standalone paragraph.",
            "It has two sentences here.",
        ]
        for t in doc.tables:
            assert _top_border(t) == ("dashed", "4")
        assert not _has_adjacent_tables(doc)

    def test_precedence_sections_over_paragraphs_and_sentences(self, stub_sentences):
        doc = _frame({"sections": True, "paragraphs": True, "sentences": True})
        # Every body paragraph belongs to the section, so only the section frame
        # is produced (no double-wrapping).
        assert len(doc.tables) == 1
        assert _top_border(doc.tables[0]) == ("double", "16")

    def test_custom_border_overrides_defaults(self):
        with tempfile.TemporaryDirectory() as d:
            inp = os.path.join(d, "in.docx")
            out = os.path.join(d, "out.docx")
            _build_doc(inp)
            get_formatting_service().apply_framing(
                inp, out,
                {"paragraphs": True, "use_tables": True,
                 "border_style": "dotted", "border_width": 12, "border_color": "#FF0000"},
            )
            doc = Document(out)
            val, sz = _top_border(doc.tables[0])
            assert val == "dotted"
            assert sz == "12"
            color = doc.tables[0]._element.find(qn('w:tblPr')).find(
                qn('w:tblBorders')).find(qn('w:top')).get(qn('w:color'))
            assert color == "FF0000"
