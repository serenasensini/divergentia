"""
Security-focused tests for file upload handling (issues #9, #10, #11):
- content-based file type validation (magic bytes), not just extension
- filename sanitisation / directory-traversal prevention
- upload size limits enforced both at the app level and via Flask's
  MAX_CONTENT_LENGTH
"""
import io
import os

from app.utils.file_handler import (
    validate_file,
    validate_file_content,
    save_uploaded_file,
)


class _FakeUpload:
    """Minimal FileStorage-like stub exposing read/seek/save."""

    def __init__(self, data: bytes, filename: str):
        self._buf = io.BytesIO(data)
        self.filename = filename

    def read(self, n=-1):
        return self._buf.read(n)

    def seek(self, pos, whence=0):
        return self._buf.seek(pos, whence)

    def tell(self):
        return self._buf.tell()

    def save(self, path):
        self._buf.seek(0)
        with open(path, 'wb') as f:
            f.write(self._buf.read())


class TestFileTypeValidation:
    """Issue #10 — content-based file type validation."""

    def test_accepts_genuine_txt_content(self):
        upload = _FakeUpload(b"Hello, this is plain text.", "note.txt")
        ok, err = validate_file_content(upload, "txt")
        assert ok is True
        assert err is None

    def test_accepts_genuine_pdf_magic_bytes(self):
        # Minimal PDF header magic bytes are enough for libmagic to say 'application/pdf'.
        pdf_bytes = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\n%%EOF"
        upload = _FakeUpload(pdf_bytes, "doc.pdf")
        ok, err = validate_file_content(upload, "pdf")
        assert ok is True

    def test_accepts_genuine_docx_zip_magic_bytes(self):
        # A real DOCX is a ZIP container; the ZIP local-file-header magic
        # ("PK\x03\x04") is enough for libmagic to classify it as zip/OOXML.
        zip_bytes = b"PK\x03\x04" + b"\x00" * 26 + b"[Content_Types].xml" + b"\x00" * 50
        upload = _FakeUpload(zip_bytes, "report.docx")
        ok, err = validate_file_content(upload, "docx")
        assert ok is True

    def test_rejects_executable_spoofed_as_docx(self):
        # ELF magic bytes ("\x7fELF"), renamed to look like a DOCX upload.
        elf_bytes = b"\x7fELF" + b"\x00" * 60
        upload = _FakeUpload(elf_bytes, "totally_a_document.docx")
        ok, err = validate_file_content(upload, "docx")
        assert ok is False
        assert "does not match" in err

    def test_rejects_script_spoofed_as_pdf(self):
        script_bytes = b"#!/bin/bash\nrm -rf /\n"
        upload = _FakeUpload(script_bytes, "invoice.pdf")
        ok, err = validate_file_content(upload, "pdf")
        assert ok is False

    def test_stream_position_restored_after_sniffing(self):
        # The full content must still be readable/saveable after validation.
        data = b"Some text content for restoring the stream position."
        upload = _FakeUpload(data, "note.txt")
        validate_file_content(upload, "txt")
        assert upload.read() == data

    def test_empty_file_rejected(self):
        upload = _FakeUpload(b"", "empty.docx")
        ok, err = validate_file_content(upload, "docx")
        assert ok is False
        assert "empty" in err.lower()

    def test_unknown_extension_is_not_content_validated(self):
        # Extension-level rejection is handled by validate_file(); content
        # sniffing should not block extensions it doesn't know about.
        upload = _FakeUpload(b"whatever", "archive.zip")
        ok, err = validate_file_content(upload, "zip")
        assert ok is True


class TestFilenameSanitisation:
    """Issue #9 — sanitise filenames / prevent directory traversal."""

    def test_path_traversal_filename_is_sanitised(self, tmp_path):
        upload_folder = str(tmp_path / "uploads")
        malicious = _FakeUpload(b"data", "../../../../etc/passwd")
        file_path, original_filename = save_uploaded_file(malicious, upload_folder)

        # The saved file must live strictly inside the upload folder.
        real_upload_folder = os.path.realpath(upload_folder)
        real_file_path = os.path.realpath(file_path)
        assert os.path.commonpath([real_upload_folder, real_file_path]) == real_upload_folder
        assert ".." not in os.path.basename(file_path)
        assert original_filename == "../../../../etc/passwd"  # preserved for display only

    def test_absolute_path_filename_is_sanitised(self, tmp_path):
        upload_folder = str(tmp_path / "uploads")
        malicious = _FakeUpload(b"data", "/etc/passwd")
        file_path, _ = save_uploaded_file(malicious, upload_folder)
        real_upload_folder = os.path.realpath(upload_folder)
        real_file_path = os.path.realpath(file_path)
        assert os.path.commonpath([real_upload_folder, real_file_path]) == real_upload_folder

    def test_filename_with_only_unsafe_characters_is_rejected(self, tmp_path):
        from app.exceptions.custom_exceptions import FileUploadException

        upload_folder = str(tmp_path / "uploads")
        malicious = _FakeUpload(b"data", "????....")
        try:
            save_uploaded_file(malicious, upload_folder)
            assert False, "Expected FileUploadException for an unsafe filename"
        except FileUploadException:
            pass

    def test_normal_filename_round_trips(self, tmp_path):
        upload_folder = str(tmp_path / "uploads")
        upload = _FakeUpload(b"hello world", "my report.docx")
        file_path, original_filename = save_uploaded_file(upload, upload_folder)
        assert os.path.exists(file_path)
        assert original_filename == "my report.docx"
        assert file_path.endswith(".docx")


class TestUploadSizeLimits:
    """Issue #11 — enforce configurable upload size limits."""

    def test_oversized_file_rejected_by_validate_file(self, app):
        with app.app_context():
            max_size = app.config['MAX_UPLOAD_SIZE']
            ok, err = validate_file("big.docx", max_size + 1)
            assert ok is False
            assert "exceeds maximum allowed size" in err

    def test_file_at_exact_limit_is_accepted(self, app):
        with app.app_context():
            max_size = app.config['MAX_UPLOAD_SIZE']
            ok, err = validate_file("big.docx", max_size)
            assert ok is True

    def test_max_content_length_is_configured(self, app):
        # Flask/Werkzeug must reject oversized request bodies at the
        # transport level (413), not only after fully reading them.
        assert app.config['MAX_CONTENT_LENGTH'] == app.config['MAX_UPLOAD_SIZE']

    def test_oversized_upload_rejected_with_413_via_http(self, app, client):
        with app.app_context():
            max_size = app.config['MAX_UPLOAD_SIZE']
        oversized = io.BytesIO(b"a" * (max_size + 1024))
        response = client.post(
            '/api/documents/upload',
            data={'file': (oversized, 'huge.txt')},
            content_type='multipart/form-data',
        )
        assert response.status_code == 413
        data = response.get_json()
        assert data['error'] == 'FileTooLarge'
        assert 'max_upload_size_mb' in data

    def test_supported_formats_surfaces_max_size(self, client):
        response = client.get('/api/formats/supported')
        assert response.status_code == 200
        data = response.get_json()
        assert 'max_upload_size_bytes' in data
        assert 'max_upload_size_mb' in data
        assert data['max_upload_size_bytes'] > 0

