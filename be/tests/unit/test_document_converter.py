"""
Unit tests for DOC/PDF -> DOCX conversion and RTF removal.

Covers roadmap items #6 (PDF), #7 (DOC) and #8 (remove RTF):
- ``needs_conversion`` classification;
- ``convert_to_docx`` command construction / success / failure handling
  (LibreOffice is mocked so the suite does not require the binary);
- RTF is no longer an accepted upload type;
- the upload endpoint converts DOC/PDF to a DOCX working file.
"""
import io
import os
from pathlib import Path

import pytest
from docx import Document

from app.utils import document_converter as dc
from app.exceptions.custom_exceptions import FileProcessingException


class TestNeedsConversion:
    def test_doc_and_pdf_need_conversion(self):
        assert dc.needs_conversion('doc') is True
        assert dc.needs_conversion('pdf') is True
        assert dc.needs_conversion('.PDF') is True

    def test_docx_and_txt_do_not(self):
        assert dc.needs_conversion('docx') is False
        assert dc.needs_conversion('txt') is False

    def test_rtf_is_not_convertible(self):
        # RTF is dropped entirely, never converted.
        assert dc.needs_conversion('rtf') is False


class TestConvertToDocx:
    def test_rejects_unsupported_extension(self, tmp_path):
        src = tmp_path / "note.txt"
        src.write_text("hello")
        with pytest.raises(FileProcessingException):
            dc.convert_to_docx(str(src), str(tmp_path))

    def test_missing_source_raises(self, tmp_path):
        with pytest.raises(FileProcessingException):
            dc.convert_to_docx(str(tmp_path / "missing.doc"), str(tmp_path))

    def test_pdf_is_converted_to_editable_paragraphs(self, tmp_path):
        # Build a real PDF with PyMuPDF, then convert it and assert the
        # resulting DOCX has real, readable paragraphs (not empty text frames).
        import fitz
        from docx import Document

        pdf_path = tmp_path / "report_ab12cd34.pdf"
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Titolo di prova")
        page.insert_text((72, 100), "Questo e un paragrafo di prova.")
        doc.save(str(pdf_path))
        doc.close()

        out = dc.convert_to_docx(str(pdf_path), str(tmp_path))

        assert out.endswith("report_ab12cd34.docx")
        assert os.path.exists(out)
        text = "\n".join(p.text for p in Document(out).paragraphs)
        assert "prova" in text.lower()

    def test_pdf_without_text_raises(self, tmp_path):
        # An empty (image-only equivalent) PDF has no extractable text.
        import fitz

        pdf_path = tmp_path / "blank_00.pdf"
        doc = fitz.open()
        doc.new_page()
        doc.save(str(pdf_path))
        doc.close()

        with pytest.raises(FileProcessingException):
            dc.convert_to_docx(str(pdf_path), str(tmp_path))

    def test_doc_conversion_uses_libreoffice(self, tmp_path, monkeypatch):
        src = tmp_path / "legacy_ef56.doc"
        src.write_bytes(b"\xd0\xcf\x11\xe0 fake doc")

        captured = {}

        monkeypatch.setattr(dc.shutil, 'which', lambda _n: "/usr/bin/soffice")

        def fake_run(cmd, **kwargs):
            captured['cmd'] = cmd
            (tmp_path / "legacy_ef56.docx").write_bytes(b"PK docx")

            class _R:
                returncode = 0
                stdout = ""
                stderr = ""
            return _R()

        monkeypatch.setattr(dc.subprocess, 'run', fake_run)

        out = dc.convert_to_docx(str(src), str(tmp_path))
        assert out.endswith("legacy_ef56.docx")
        assert '--convert-to' in captured['cmd']
        assert 'docx:MS Word 2007 XML' in captured['cmd']

    def test_nonzero_return_code_raises(self, tmp_path, monkeypatch):
        src = tmp_path / "broken_00.doc"
        src.write_bytes(b"bad")

        monkeypatch.setattr(dc.shutil, 'which', lambda _n: "/usr/bin/soffice")

        def fake_run(cmd, **kwargs):
            class _R:
                returncode = 1
                stdout = ""
                stderr = "conversion error"
            return _R()

        monkeypatch.setattr(dc.subprocess, 'run', fake_run)

        with pytest.raises(FileProcessingException):
            dc.convert_to_docx(str(src), str(tmp_path))


class TestAllowedExtensions:
    def test_rtf_not_allowed(self, app):
        assert 'rtf' not in app.config['ALLOWED_EXTENSIONS']

    def test_expected_formats_allowed(self, app):
        allowed = app.config['ALLOWED_EXTENSIONS']
        assert {'pdf', 'docx', 'doc', 'txt'} <= allowed


class TestUploadConversion:
    def test_rtf_upload_rejected(self, client):
        data = {'file': (io.BytesIO(b'{\\rtf1 hello}'), 'note.rtf')}
        resp = client.post(
            '/api/documents/upload', data=data,
            content_type='multipart/form-data'
        )
        assert resp.status_code == 400

    def test_pdf_upload_is_converted_to_docx(self, client, monkeypatch):
        # Mock the conversion so the test does not require LibreOffice: it
        # writes a fake DOCX next to the uploaded source and returns its path.
        import app.blueprints.documents.routes as routes

        def fake_convert(src_path, out_dir):
            produced = Path(out_dir) / (Path(src_path).stem + '.docx')
            produced.write_bytes(b'PK fake docx')
            return str(produced)

        monkeypatch.setattr(routes, 'convert_to_docx', fake_convert)

        data = {'file': (io.BytesIO(b'%PDF-1.4 fake'), 'invoice.pdf')}
        resp = client.post(
            '/api/documents/upload', data=data,
            content_type='multipart/form-data'
        )
        assert resp.status_code == 201
        body = resp.get_json()
        # The working file is now a DOCX; the user-facing name reflects it.
        assert body['original_filename'] == 'invoice.docx'
        assert body['file_extension'] == 'docx'

