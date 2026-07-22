"""
Unit tests for DocumentService operation chaining and finalize behaviour.

These verify that calling multiple processing endpoints in sequence on the same
document accumulates changes (each op reads the previous op's output), that the
``from_original`` flag resets to the uploaded file, and that responses expose
``document_id``/``download_url`` instead of the raw server path.
"""
import pytest

from app.services.document_service import DocumentService
from app.repositories.document_repository import DocumentRepository


class FakeFormattingService:
    """Records the input path each operation reads from and writes a marker."""

    def __init__(self):
        self.calls = []

    def _run(self, op, input_path, output_path, options):
        self.calls.append({'op': op, 'input': input_path, 'output': output_path})
        return {'success': True, 'output_path': output_path, 'op': op}

    def apply_spacing(self, input_path, output_path, options):
        return self._run('spacing', input_path, output_path, options)

    def apply_framing(self, input_path, output_path, options):
        return self._run('framing', input_path, output_path, options)

    def apply_formatting(self, input_path, output_path, options):
        return self._run('formatting', input_path, output_path, options)


@pytest.fixture
def service(tmp_path):
    repo = DocumentRepository()
    svc = DocumentService.__new__(DocumentService)
    svc.repository = repo
    svc.formatting_service = FakeFormattingService()
    svc.ollama_service = None
    return svc


@pytest.fixture
def document(service):
    return service.create_document(
        file_path='/uploads/original.docx',
        original_filename='original.docx',
        file_size=123,
        mime_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    )


def test_finalize_response_shape(service, document, tmp_path):
    out = str(tmp_path / "out")
    resp = service.apply_spacing(document['id'], {'paragraphs': True}, out)

    assert resp['document_id'] == document['id']
    assert 'download_url' in resp
    assert resp['download_url'] == f"/api/documents/{document['id']}/download"
    assert 'filename' in resp
    # Raw server path must not leak to the client
    assert 'output_path' not in resp


def test_first_operation_reads_original(service, document, tmp_path):
    out = str(tmp_path / "out")
    service.apply_spacing(document['id'], {'paragraphs': True}, out)

    first_call = service.formatting_service.calls[0]
    assert first_call['input'] == '/uploads/original.docx'


def test_second_operation_chains_from_first(service, document, tmp_path):
    out = str(tmp_path / "out")
    service.apply_spacing(document['id'], {'paragraphs': True}, out)
    service.apply_framing(document['id'], {'paragraphs': True}, out)

    spacing_call, framing_call = service.formatting_service.calls
    # Framing must read the file spacing produced (chaining), not the original.
    assert framing_call['input'] == spacing_call['output']
    assert framing_call['input'] != '/uploads/original.docx'


def test_formatted_path_persisted(service, document, tmp_path):
    out = str(tmp_path / "out")
    service.apply_spacing(document['id'], {'paragraphs': True}, out)

    stored = service.get_document(document['id'])
    spacing_output = service.formatting_service.calls[0]['output']
    assert stored['formatted_path'] == spacing_output


def test_from_original_resets_chain(service, document, tmp_path):
    out = str(tmp_path / "out")
    service.apply_spacing(document['id'], {'paragraphs': True}, out)
    # Even though a processed version now exists, from_original ignores it.
    service.apply_framing(document['id'], {'paragraphs': True, 'from_original': True}, out)

    framing_call = service.formatting_service.calls[1]
    assert framing_call['input'] == '/uploads/original.docx'
