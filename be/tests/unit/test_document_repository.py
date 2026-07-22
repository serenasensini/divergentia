"""
Unit tests for the in-memory DocumentRepository.

The registry is ephemeral (single-shot local usage): records live only for the
lifetime of the process and are never persisted.
"""
import pytest

from app.repositories.document_repository import DocumentRepository


@pytest.fixture
def repo():
    return DocumentRepository()


def _doc(doc_id="doc-1"):
    return {
        'id': doc_id,
        'original_filename': 'sample.docx',
        'file_path': '/uploads/sample.docx',
        'formatted_path': None,
        'text_content': None,
    }


def test_create_and_get(repo):
    repo.create(_doc())
    fetched = repo.get("doc-1")
    assert fetched is not None
    assert fetched['original_filename'] == 'sample.docx'


def test_get_missing_returns_none(repo):
    assert repo.get("nope") is None


def test_update_merges_fields(repo):
    repo.create(_doc())
    updated = repo.update("doc-1", {'formatted_path': '/outputs/spacing_sample.docx'})
    assert updated['formatted_path'] == '/outputs/spacing_sample.docx'
    # original fields are preserved
    assert updated['original_filename'] == 'sample.docx'
    # persisted for subsequent reads
    assert repo.get("doc-1")['formatted_path'] == '/outputs/spacing_sample.docx'


def test_update_missing_returns_none(repo):
    assert repo.update("nope", {'x': 1}) is None


def test_delete(repo):
    repo.create(_doc())
    assert repo.delete("doc-1") is True
    assert repo.get("doc-1") is None
    assert repo.delete("doc-1") is False


def test_get_returns_copy(repo):
    repo.create(_doc())
    fetched = repo.get("doc-1")
    fetched['formatted_path'] = '/tmp/mutated.docx'
    # Mutating the returned dict must not affect the stored record.
    assert repo.get("doc-1")['formatted_path'] is None


def test_instances_are_independent(repo):
    # Ephemeral: a separate instance shares no state (nothing persisted).
    repo.create(_doc("shared-id"))
    other = DocumentRepository()
    assert other.get("shared-id") is None


def test_count_and_list(repo):
    repo.create(_doc("a"))
    repo.create(_doc("b"))
    assert repo.count() == 2
    ids = {d['id'] for d in repo.list_all()}
    assert ids == {"a", "b"}
