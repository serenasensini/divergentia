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
from app.utils.text_extractor import extract_text_from_file
from app.exceptions.custom_exceptions import (
    DocumentNotFoundException,
    FileProcessingException
)

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for managing document operations"""

    def __init__(self):
        """Initialize document service"""
        self.ollama_service = get_ollama_service()
        self.formatting_service = get_formatting_service()

        # In-memory document storage (replace with database in production)
        self._documents: Dict[str, Dict[str, Any]] = {}

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
            'created_at': None,  # Add timestamp in production
            'modified_at': None,
            'text_content': None,
            'formatted_path': None
        }

        self._documents[document_id] = document
        logger.info(f"Document created with ID: {document_id}")
        logger.debug(f"Listing all documents after creation: {list(self._documents.keys())}")

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
        logger.debug(f"Listing all documents: {list(self._documents.keys())}")
        logger.info(f"Retrieving document with ID: {document_id}")
        if document_id not in self._documents:
            raise DocumentNotFoundException(document_id)

        return self._documents[document_id]

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

            # Store text content in document
            document['text_content'] = text_content

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

        # Generate output path
        output_filename = f"formatted_{document['original_filename']}"
        output_path = os.path.join(output_folder, output_filename)

        # Apply formatting
        result = self.formatting_service.apply_formatting(
            document['file_path'],
            output_path,
            formatting_options
        )

        # Update document record
        document['formatted_path'] = output_path
        document['modified_at'] = None  # Add timestamp in production

        return result

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

        # Generate output path with "edited_" prefix
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"edited_{timestamp}_{document['original_filename']}"
        output_path = os.path.join(output_folder, output_filename)

        # Apply framing
        result = self.formatting_service.apply_framing(
            document['file_path'],
            output_path,
            framing_options
        )

        # Update document record
        document['formatted_path'] = output_path
        document['modified_at'] = None  # Add timestamp in production

        return result

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

        # Generate output path with "edited_" prefix
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"spacing_{timestamp}_{document['original_filename']}"
        output_path = os.path.join(output_folder, output_filename)

        # Apply framing
        result = self.formatting_service.apply_spacing(
            document['file_path'],
            output_path,
            spacing_options
        )

        # Update document record
        document['formatted_path'] = output_path
        document['modified_at'] = None  # Add timestamp in production

        return result

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

        # Generate output path with "keywords_" prefix
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"keywords_{timestamp}_{document['original_filename']}"
        output_path = os.path.join(output_folder, output_filename)

        # Apply keyword extraction
        result = self.formatting_service.apply_keywords(
            document['file_path'],
            output_path,
            keyword_options
        )

        # Update document record
        document['formatted_path'] = output_path
        document['modified_at'] = None  # Add timestamp in production

        return result

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

        # Generate output path with "highlighted_" prefix
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"highlighted_{timestamp}_{document['original_filename']}"
        output_path = os.path.join(output_folder, output_filename)

        # Apply highlighting
        result = self.formatting_service.apply_highlighting(
            document['file_path'],
            output_path,
            highlighting_options
        )

        # Update document record
        document['formatted_path'] = output_path
        document['modified_at'] = None  # Add timestamp in production

        return result

# FIXME include a percentage for needed summarization
    def summarize_document(
        self,
        document_id: str,
        summary_type: str = 'brief'
    ) -> Dict[str, Any]:
        """
        Generate summary of document.

        Args:
            document_id: Document ID
            summary_type: Type of summary

        Returns:
            Summary information
        """
        logger.info(f"Summarizing document {document_id} (type: {summary_type})")

        document = self.get_document(document_id)

        # Extract text if not already done
        if not document.get('text_content'):
            self.extract_text(document_id)

        text_content = document['text_content']

        # Generate summary using Ollama
        summary_result = self.ollama_service.summarize_document(
            text_content,
            summary_type=summary_type
        )

        return {
            'document_id': document_id,
            'document_name': document['original_filename'],
            **summary_result
        }


    def paraphrase_document(
        self,
        document_id: str,
        style: str = 'formal',
        sections: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Paraphrase document or specific sections.

        Args:
            document_id: Document ID
            style: Paraphrasing style
            sections: Optional list of section indices to paraphrase

        Returns:
            Paraphrased content
        """
        logger.info(f"Paraphrasing document {document_id} (style: {style})")

        document = self.get_document(document_id)

        # Extract text if not already done
        if not document.get('text_content'):
            self.extract_text(document_id)

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
                        style=style
                    )
        else:
            # Paraphrase all chunks
            paraphrased_chunks = self.ollama_service.batch_paraphrase(
                chunks,
                style=style
            )
            paraphrased_sections = {
                idx: text for idx, text in enumerate(paraphrased_chunks)
            }

        return {
            'document_id': document_id,
            'document_name': document['original_filename'],
            'style': style,
            'total_sections': len(chunks),
            'paraphrased_sections': paraphrased_sections
        }

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
        del self._documents[document_id]

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
