"""
Document Service - Main business logic for document operations
"""
import datetime
import logging
import os
import uuid
from typing import Dict, Any, Optional
from pathlib import Path

from app.services.ollama_service import get_ollama_service
from app.services.formatting_service import get_formatting_service
from app.repositories.document_repository import DocumentRepository, get_repository
from app.utils.text_extractor import extract_text_from_file
from app.utils.file_handler import cap_filename
from app.exceptions.custom_exceptions import (
    DocumentNotFoundException,
    FileProcessingException
)

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for managing document operations"""

    def __init__(self, repository: Optional[DocumentRepository] = None) -> None:
        """Initialize document service.

        Args:
            repository: Optional document repository. Defaults to the shared
                SQLite-backed registry so records persist across restarts and
                are shared across workers.
        """
        self.ollama_service = get_ollama_service()
        self.formatting_service = get_formatting_service()

        # Persistent document registry (SQLite-backed).
        self.repository = repository or get_repository()

        logger.info("Document service initialized")

    def create_document(
        self,
        file_path: str,
        original_filename: str,
        file_size: int,
        mime_type: str
    ) -> Dict[str, Any]:
        """
        Create a new document record.

        Args:
            file_path: Path where file is stored
            original_filename: Original filename
            file_size: File size in bytes
            mime_type: MIME type of file

        Returns:
            Document metadata
        """
        document_id = str(uuid.uuid4())

        document = {
            'id': document_id,
            'original_filename': original_filename,
            'file_path': file_path,
            'file_size': file_size,
            'mime_type': mime_type,
            'file_extension': Path(original_filename).suffix.lower().lstrip('.'),
            'created_at': datetime.datetime.now().isoformat(),
            'modified_at': None,
            'text_content': None,
            'formatted_path': None
        }

        self.repository.create(document)
        logger.info(f"Document created with ID: {document_id}")

        return document

    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document metadata

        Raises:
            DocumentNotFoundException: If document not found
        """
        logger.info(f"Retrieving document with ID: {document_id}")
        document = self.repository.get(document_id)
        if document is None:
            raise DocumentNotFoundException(document_id)

        return document

    def _source_path(self, document: Dict[str, Any], from_original: bool = False) -> str:
        """Return the path an operation should read from.

        By default operations chain: each one reads the latest processed version
        (``formatted_path``) so multiple endpoints called in sequence accumulate
        their changes into a single output. Pass ``from_original=True`` to ignore
        previous processing and start again from the uploaded file.

        Args:
            document: Document record.
            from_original: When True, always read the original uploaded file.

        Returns:
            The filesystem path to use as the operation's input.
        """
        if from_original:
            return document['file_path']
        return document.get('formatted_path') or document['file_path']

    def _finalize(
        self,
        document: Dict[str, Any],
        output_path: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Persist the new processed version and build a client-facing response.

        Records ``output_path`` as the document's latest ``formatted_path`` so a
        subsequent operation chains from it and ``/download`` serves it. The
        response returns the ``document_id`` and a ``download_url`` (not the raw
        server path), so the front-end can download by id after any number of
        chained operations.

        Args:
            document: Document record being processed.
            output_path: Path of the freshly written processed file.
            result: Raw result from the formatting service.

        Returns:
            Client-facing response dictionary.
        """
        self.repository.update(document['id'], {
            'formatted_path': output_path,
            'modified_at': datetime.datetime.now().isoformat(),
        })

        response = {k: v for k, v in result.items() if k != 'output_path'}
        response['document_id'] = document['id']
        response['filename'] = os.path.basename(output_path)
        response['download_url'] = f"/api/documents/{document['id']}/download"
        return response

# FIXME review text extraction logic and error handling, consider edge cases (e.g. unsupported formats, large files)
    def extract_text(self, document_id: str) -> Dict[str, Any]:
        """
        Extract text content from document.

        Args:
            document_id: Document ID

        Returns:
            Dictionary with extracted text

        Raises:
            DocumentNotFoundException: If document not found
            FileProcessingException: If extraction fails
        """
        logger.info(f"Extracting text from document {document_id}")

        document = self.get_document(document_id)

        try:
            text_content = extract_text_from_file(document['file_path'])

            # Persist extracted text on the record
            self.repository.update(document_id, {'text_content': text_content})

            return {
                'document_id': document_id,
                'text_content': text_content,
                'character_count': len(text_content),
                'word_count': len(text_content.split())
            }

        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise FileProcessingException(f"Failed to extract text: {str(e)}")

#     FIXME: review formatting options and result structure
    def apply_formatting(
        self,
        document_id: str,
        formatting_options: Dict[str, Any],
        output_folder: str
    ) -> Dict[str, Any]:
        """
        Apply formatting to document.

        Args:
            document_id: Document ID
            formatting_options: Formatting options
            output_folder: Folder to save formatted document

        Returns:
            Dictionary with result information
        """
        logger.info(f"Applying formatting to document {document_id}")

        document = self.get_document(document_id)
        from_original = formatting_options.pop('from_original', False)

        # Generate output path
        output_filename = cap_filename(f"formatted_{document['original_filename']}")
        output_path = os.path.join(output_folder, output_filename)

        # Apply formatting, chaining from the latest processed version
        result = self.formatting_service.apply_formatting(
            self._source_path(document, from_original),
            output_path,
            formatting_options
        )

        return self._finalize(document, output_path, result)

    def apply_framing(
        self,
        document_id: str,
        framing_options: Dict[str, bool],
        output_folder: str
    ) -> Dict[str, Any]:
        """
        Apply framing (borders) to document parts.

        Args:
            document_id: Document ID
            framing_options: Framing options (sections, paragraphs, etc.)
            output_folder: Folder to save framed document

        Returns:
            Dictionary with result information
        """
        logger.info(f"Applying framing to document {document_id}")

        document = self.get_document(document_id)
        from_original = framing_options.pop('from_original', False)

        # Generate output path with "edited_" prefix
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = cap_filename(f"edited_{timestamp}_{document['original_filename']}")
        output_path = os.path.join(output_folder, output_filename)

        # Apply framing, chaining from the latest processed version
        result = self.formatting_service.apply_framing(
            self._source_path(document, from_original),
            output_path,
            framing_options
        )

        return self._finalize(document, output_path, result)

    def apply_spacing(
        self,
        document_id: str,
        spacing_options: Dict[str, bool],
        output_folder: str
    ) -> Dict[str, Any]:
        """
        Apply spacing adjustments to document parts.

        Args:
            document_id: Document ID
            spacing_options: Spacing options (paragraphs, senteces)
            output_folder: Folder to save framed document

        Returns:
            Dictionary with result information
        """
        logger.info(f"Applying spacing to document {document_id}")

        document = self.get_document(document_id)
        from_original = spacing_options.pop('from_original', False)

        # Generate output path with "spacing_" prefix
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = cap_filename(f"spacing_{timestamp}_{document['original_filename']}")
        output_path = os.path.join(output_folder, output_filename)

        # Apply spacing, chaining from the latest processed version
        result = self.formatting_service.apply_spacing(
            self._source_path(document, from_original),
            output_path,
            spacing_options
        )

        return self._finalize(document, output_path, result)

    def apply_keywords(
        self,
        document_id: str,
        keyword_options: Dict[str, Any],
        output_folder: str
    ) -> Dict[str, Any]:
        """
        Extract keywords from document sections and add them as initial paragraphs.

        Args:
            document_id: Document ID
            keyword_options: Keyword extraction options (max_keywords, include_proper_nouns)
            output_folder: Folder to save processed document

        Returns:
            Dictionary with result information
        """
        logger.info(f"Applying keyword extraction to document {document_id}")

        document = self.get_document(document_id)
        from_original = keyword_options.pop('from_original', False)

        # Generate output path with "keywords_" prefix
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = cap_filename(f"keywords_{timestamp}_{document['original_filename']}")
        output_path = os.path.join(output_folder, output_filename)

        # Apply keyword extraction, chaining from the latest processed version
        result = self.formatting_service.apply_keywords(
            self._source_path(document, from_original),
            output_path,
            keyword_options
        )

        return self._finalize(document, output_path, result)

    def apply_highlighting(
        self,
        document_id: str,
        highlighting_options: Dict[str, Any],
        output_folder: str
    ) -> Dict[str, Any]:
        """
        Apply part-of-speech highlighting to document.

        Args:
            document_id: Document ID
            highlighting_options: Highlighting options (enabled, color, nouns, verbs, adjectives, adverbs)
            output_folder: Folder to save processed document

        Returns:
            Dictionary with result information
        """
        logger.info(f"Applying part-of-speech highlighting to document {document_id}")

        document = self.get_document(document_id)
        from_original = highlighting_options.pop('from_original', False)

        # Generate output path with "highlighted_" prefix
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = cap_filename(f"highlighted_{timestamp}_{document['original_filename']}")
        output_path = os.path.join(output_folder, output_filename)

        # Apply highlighting, chaining from the latest processed version
        result = self.formatting_service.apply_highlighting(
            self._source_path(document, from_original),
            output_path,
            highlighting_options
        )

        return self._finalize(document, output_path, result)

# FIXME include a percentage for needed summarization
    def summarize_document(
        self,
        document_id: str,
        summary_type: str = 'brief',
        add_to_document: bool = False,
        output_folder: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate summary of document.

        Args:
            document_id: Document ID
            summary_type: Type of summary
            add_to_document: When True, the generated summary is inserted at the
                top of the document (after the title, before the body content)
                and a new processed version is produced.
            output_folder: Folder to save the processed document. Required when
                ``add_to_document`` is True.
            model: Optional Ollama model tag to use for this request (FE "AI
                model tier" selector, see issue #22). Falls back to the
                server's configured default model when omitted.

        Returns:
            Summary information. When ``add_to_document`` is True the response
            also contains ``download_url`` and ``filename`` for the updated file.
        """
        logger.info(f"Summarizing document {document_id} (type: {summary_type})")

        document = self.get_document(document_id)

        # Extract text if not already done
        if not document.get('text_content'):
            self.extract_text(document_id)
            document = self.get_document(document_id)

        text_content = document['text_content']

        # Generate summary using Ollama
        summary_result = self.ollama_service.summarize_document(
            text_content,
            summary_type=summary_type,
            model=model
        )

        response = {
            'document_id': document_id,
            'document_name': document['original_filename'],
            **summary_result
        }

        # Optionally insert the summary at the top of the document.
        if add_to_document:
            if not output_folder:
                raise FileProcessingException(
                    "output_folder is required to add the summary to the document"
                )

            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            output_filename = cap_filename(
                f"summarized_{timestamp}_{document['original_filename']}"
            )
            output_path = os.path.join(output_folder, output_filename)

            # Insert into the latest processed version so it chains with any
            # previous operations.
            insert_result = self.formatting_service.insert_summary(
                self._source_path(document),
                output_path,
                summary_result['summary']
            )

            finalized = self._finalize(document, output_path, insert_result)
            # Merge the download metadata into the summary response.
            response.update({
                'download_url': finalized.get('download_url'),
                'filename': finalized.get('filename'),
                'added_to_document': True,
            })

        return response


    def paraphrase_document(
        self,
        document_id: str,
        style: str = 'formal',
        sections: Optional[list] = None,
        apply_to_document: bool = False,
        output_folder: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Paraphrase document or specific sections.

        Args:
            document_id: Document ID
            style: Paraphrasing style
            sections: Optional list of section indices to paraphrase
            apply_to_document: When True, the paraphrase is written back into the
                document body (rewriting the content in place, preserving titles
                and headings) and a new processed version is produced.
            output_folder: Folder to save the processed document. Required when
                ``apply_to_document`` is True.
            model: Optional Ollama model tag to use for this request (FE "AI
                model tier" selector, see issue #22). Falls back to the
                server's configured default model when omitted.

        Returns:
            Paraphrased content. When ``apply_to_document`` is True the response
            also contains ``download_url`` and ``filename`` for the updated file.
        """
        logger.info(f"Paraphrasing document {document_id} (style: {style})")

        document = self.get_document(document_id)

        # Extract text if not already done
        if not document.get('text_content'):
            self.extract_text(document_id)
            document = self.get_document(document_id)

        text_content = document['text_content']

        # Chunk text for processing
        chunks = self.ollama_service.chunk_text(text_content)

        # Paraphrase specific sections or all
        if sections:
            # Paraphrase only specified sections
            paraphrased_sections = {}
            for idx in sections:
                if 0 <= idx < len(chunks):
                    paraphrased_sections[idx] = self.ollama_service.paraphrase_text(
                        chunks[idx],
                        style=style,
                        model=model
                    )
        else:
            # Paraphrase all chunks
            paraphrased_chunks = self.ollama_service.batch_paraphrase(
                chunks,
                style=style,
                model=model
            )
            paraphrased_sections = {
                idx: text for idx, text in enumerate(paraphrased_chunks)
            }

        response = {
            'document_id': document_id,
            'document_name': document['original_filename'],
            'style': style,
            'total_sections': len(chunks),
            'paraphrased_sections': paraphrased_sections
        }

        # Optionally rewrite the document body with the paraphrased text.
        if apply_to_document:
            if not output_folder:
                raise FileProcessingException(
                    "output_folder is required to apply the paraphrase to the document"
                )

            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            output_filename = cap_filename(
                f"paraphrased_{timestamp}_{document['original_filename']}"
            )
            output_path = os.path.join(output_folder, output_filename)

            # Rewrite the latest processed version so it chains with any
            # previous operations.
            paraphrase_result = self.formatting_service.apply_paraphrase(
                self._source_path(document),
                output_path,
                {'style': style}
            )

            finalized = self._finalize(document, output_path, paraphrase_result)
            # Merge the download metadata into the paraphrase response.
            response.update({
                'download_url': finalized.get('download_url'),
                'filename': finalized.get('filename'),
                'applied_to_document': True,
            })

        return response

    def delete_document(self, document_id: str) -> bool:
        """
        Delete document and associated files.

        Args:
            document_id: Document ID

        Returns:
            True if deleted successfully
        """
        logger.info(f"Deleting document {document_id}")

        document = self.get_document(document_id)

        # Delete files
        try:
            if os.path.exists(document['file_path']):
                os.remove(document['file_path'])

            if document.get('formatted_path') and os.path.exists(document['formatted_path']):
                os.remove(document['formatted_path'])
        except Exception as e:
            logger.error(f"Error deleting files: {str(e)}")

        # Remove from storage
        self.repository.delete(document_id)

        logger.info(f"Document {document_id} deleted")
        return True


# Singleton instance
_document_service_instance: Optional[DocumentService] = None


def get_document_service() -> DocumentService:
    """
    Get or create DocumentService singleton instance.

    Returns:
        DocumentService instance (singleton)
    """
    global _document_service_instance

    if _document_service_instance is None:
        _document_service_instance = DocumentService()
        logger.info("Document service singleton instance created")

    return _document_service_instance
