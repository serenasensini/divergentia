"""
Document Formatting Service - Handle document style modifications
"""
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import PyPDF2
import pymupdf  # PyMuPDF

from app.exceptions.custom_exceptions import (
    FormattingException,
    FileProcessingException
)

logger = logging.getLogger(__name__)


class FormattingService:
    """Service for applying formatting changes to documents"""

    SUPPORTED_FORMATS = {
        'docx': ['font_name', 'font_size', 'font_color', 'bold', 'italic', 'alignment', 'framing'],
        'pdf': ['font_name', 'font_size', 'font_color', 'framing'],  # Limited PDF support
        'txt': []  # Plain text has no formatting
    }

    # Default border specifications
    DEFAULT_BORDER_WIDTH = 4  # 1/2 pt = 4 eighths of a point
    DEFAULT_BORDER_COLOR = "000000"  # Black
    DEFAULT_BORDER_STYLE = "single"  # Solid line

    def __init__(self):
        """Initialize formatting service"""
        logger.info("Formatting service initialized")

    def apply_formatting(
        self,
        input_path: str,
        output_path: str,
        formatting_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply formatting changes to a document.

        Args:
            input_path: Path to input document
            output_path: Path to save formatted document
            formatting_options: Dictionary with formatting options

        Returns:
            Dictionary with result information

        Raises:
            FormattingException: If formatting fails
        """
        logger.info(f"Applying formatting to {input_path}")

        # Determine file type
        file_extension = Path(input_path).suffix.lower().lstrip('.')

        if file_extension not in self.SUPPORTED_FORMATS:
            raise FormattingException(
                f"Unsupported file format: {file_extension}",
                payload={'supported_formats': list(self.SUPPORTED_FORMATS.keys())}
            )

        # Apply formatting based on file type
        try:
            if file_extension == 'docx':
                return self._format_docx(input_path, output_path, formatting_options)
            elif file_extension == 'pdf':
                return self._format_pdf(input_path, output_path, formatting_options)
            elif file_extension == 'txt':
                return self._format_txt(input_path, output_path, formatting_options)
            else:
                raise FormattingException(f"Handler not implemented for {file_extension}")

        except Exception as e:
            logger.error(f"Formatting error: {str(e)}")
            raise FormattingException(f"Failed to apply formatting: {str(e)}")

    def apply_framing(
        self,
        input_path: str,
        output_path: str,
        framing_options: Dict[str, bool]
    ) -> Dict[str, Any]:
        """
        Apply framing (borders) to document parts.

        Args:
            input_path: Path to input document
            output_path: Path to save framed document
            framing_options: Dictionary with boolean flags for each document part

        Returns:
            Dictionary with result information

        Raises:
            FormattingException: If framing fails
        """
        logger.info(f"Applying framing to {input_path}")

        # Determine file type
        file_extension = Path(input_path).suffix.lower().lstrip('.')

        if file_extension not in self.SUPPORTED_FORMATS:
            raise FormattingException(
                f"Unsupported file format: {file_extension}",
                payload={'supported_formats': list(self.SUPPORTED_FORMATS.keys())}
            )

        # Apply framing based on file type
        try:
            if file_extension == 'docx':
                return self._apply_framing_docx(input_path, output_path, framing_options)
            elif file_extension == 'pdf':
                return self._apply_framing_pdf(input_path, output_path, framing_options)
            else:
                raise FormattingException(f"Framing not supported for {file_extension}")

        except Exception as e:
            logger.error(f"Framing error: {str(e)}")
            raise FormattingException(f"Failed to apply framing: {str(e)}")

    def _format_docx(
        self,
        input_path: str,
        output_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format DOCX document.

        Args:
            input_path: Input file path
            output_path: Output file path
            options: Formatting options

        Returns:
            Result information
        """
        logger.info("Formatting DOCX document")

        try:
            doc = Document(input_path)
            paragraphs_modified = 0

            # Extract formatting options
            font_name = options.get('font_name')
            font_size = options.get('font_size')
            font_color = options.get('font_color')
            bold = options.get('bold')
            italic = options.get('italic')
            alignment = options.get('alignment')

            # Apply to all paragraphs
            for paragraph in doc.paragraphs:
                if not paragraph.runs:
                    continue

                # Apply paragraph-level formatting
                if alignment:
                    alignment_map = {
                        'left': WD_ALIGN_PARAGRAPH.LEFT,
                        'center': WD_ALIGN_PARAGRAPH.CENTER,
                        'right': WD_ALIGN_PARAGRAPH.RIGHT,
                        'justify': WD_ALIGN_PARAGRAPH.JUSTIFY
                    }
                    if alignment.lower() in alignment_map:
                        paragraph.alignment = alignment_map[alignment.lower()]

                # Apply run-level formatting
                for run in paragraph.runs:
                    if font_name:
                        run.font.name = font_name

                    if font_size:
                        run.font.size = Pt(int(font_size))

                    if font_color:
                        # Parse color (hex format: #RRGGBB)
                        color = self._parse_color(font_color)
                        if color:
                            run.font.color.rgb = RGBColor(*color)

                    if bold is not None:
                        run.font.bold = bool(bold)

                    if italic is not None:
                        run.font.italic = bool(italic)

                paragraphs_modified += 1

            # Save document
            doc.save(output_path)

            logger.info(f"DOCX formatting completed: {paragraphs_modified} paragraphs modified")

            return {
                'success': True,
                'output_path': output_path,
                'format': 'docx',
                'paragraphs_modified': paragraphs_modified,
                'applied_options': options
            }

        except Exception as e:
            logger.error(f"DOCX formatting error: {str(e)}")
            raise FormattingException(f"DOCX formatting failed: {str(e)}")

    def _format_pdf(
        self,
        input_path: str,
        output_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format PDF document (limited support - creates new PDF with styling).

        Note: PDF formatting is limited. This creates a new styled version.

        Args:
            input_path: Input file path
            output_path: Output file path
            options: Formatting options

        Returns:
            Result information
        """
        logger.info("Formatting PDF document")
        logger.warning("PDF formatting has limited support")

        try:
            # Open PDF
            doc = pymupdf.open(input_path)
            pages_processed = 0

            # Extract formatting options
            font_name = options.get('font_name', 'helv')
            font_size = options.get('font_size', 11)
            font_color = options.get('font_color', '#000000')

            # Parse color
            color_rgb = self._parse_color(font_color)
            color_tuple = tuple(c / 255.0 for c in color_rgb) if color_rgb else (0, 0, 0)

            # Create new PDF with styling
            output_doc = pymupdf.open()

            for page in doc:
                # Extract text
                text = page.get_text()

                # Create new page
                new_page = output_doc.new_page(width=page.rect.width, height=page.rect.height)

                # Insert text with new formatting
                rect = pymupdf.Rect(50, 50, page.rect.width - 50, page.rect.height - 50)
                new_page.insert_textbox(
                    rect,
                    text,
                    fontsize=float(font_size),
                    fontname=font_name,
                    color=color_tuple
                )

                pages_processed += 1

            # Save output
            output_doc.save(output_path)
            output_doc.close()
            doc.close()

            logger.info(f"PDF formatting completed: {pages_processed} pages processed")

            return {
                'success': True,
                'output_path': output_path,
                'format': 'pdf',
                'pages_processed': pages_processed,
                'applied_options': options,
                'note': 'PDF formatting support is limited'
            }

        except Exception as e:
            logger.error(f"PDF formatting error: {str(e)}")
            raise FormattingException(f"PDF formatting failed: {str(e)}")

    def _format_txt(
        self,
        input_path: str,
        output_path: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle TXT files (no formatting, just copy).

        Args:
            input_path: Input file path
            output_path: Output file path
            options: Formatting options (ignored for txt)

        Returns:
            Result information
        """
        logger.info("Processing TXT document (no formatting applied)")

        try:
            # Copy file
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                'success': True,
                'output_path': output_path,
                'format': 'txt',
                'note': 'Plain text files do not support formatting'
            }

        except Exception as e:
            logger.error(f"TXT processing error: {str(e)}")
            raise FormattingException(f"TXT processing failed: {str(e)}")

    def _parse_color(self, color_str: str) -> Optional[tuple]:
        """
        Parse color string to RGB tuple.

        Args:
            color_str: Color string (hex format: #RRGGBB or RRGGBB)

        Returns:
            RGB tuple or None
        """
        try:
            # Remove # if present
            color_str = color_str.lstrip('#')

            # Parse hex to RGB
            r = int(color_str[0:2], 16)
            g = int(color_str[2:4], 16)
            b = int(color_str[4:6], 16)

            return (r, g, b)

        except (ValueError, IndexError) as e:
            logger.warning(f"Invalid color format: {color_str}")
            return None

    def _add_paragraph_border(self, paragraph) -> None:
        """
        Add border to a paragraph.

        Args:
            paragraph: python-docx paragraph object
        """
        pPr = paragraph._element.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')

        for border_name in ['top', 'left', 'bottom', 'right']:
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), self.DEFAULT_BORDER_STYLE)
            border.set(qn('w:sz'), str(self.DEFAULT_BORDER_WIDTH))
            border.set(qn('w:space'), '1')
            border.set(qn('w:color'), self.DEFAULT_BORDER_COLOR)
            pBdr.append(border)

        pPr.append(pBdr)

    def _identify_sections(self, doc: Document) -> List[Tuple[int, int]]:
        """
        Identify sections in document.
        Sections are identified by lines starting with space + capital letter (e.g., " A.")
        and ending at period followed by line break.

        Args:
            doc: python-docx Document object

        Returns:
            List of tuples (start_paragraph_index, end_paragraph_index)
        """
        sections = []
        current_section_start = None

        for i, para in enumerate(doc.paragraphs):
            text = para.text

            # Check if paragraph starts a section (e.g., " A. ", " B. ")
            if re.match(r'^\s+[A-Z]\.', text):
                if current_section_start is not None:
                    # Close previous section
                    sections.append((current_section_start, i - 1))
                current_section_start = i

            # Check if paragraph ends a section (ends with period and next is line break/empty)
            elif current_section_start is not None:
                if text.strip().endswith('.'):
                    # Check if next paragraph starts new section or is empty
                    if i + 1 >= len(doc.paragraphs) or not doc.paragraphs[i + 1].text.strip():
                        sections.append((current_section_start, i))
                        current_section_start = None

        # Close last section if open
        if current_section_start is not None:
            sections.append((current_section_start, len(doc.paragraphs) - 1))

        logger.info(f"Identified {len(sections)} sections")
        return sections

    def _identify_paragraphs(self, doc: Document) -> List[int]:
        """
        Identify paragraphs in document.
        A paragraph is a set of subparagraphs (groups of text separated by double line breaks).

        Args:
            doc: python-docx Document object

        Returns:
            List of paragraph indices
        """
        paragraphs = []

        for i, para in enumerate(doc.paragraphs):
            if para.text.strip():  # Non-empty paragraph
                paragraphs.append(i)

        logger.info(f"Identified {len(paragraphs)} paragraphs")
        logger.debug(f"Example of identified paragraphs: {[doc.paragraphs[i].text[:30] for i in paragraphs[:3]]}")
        return paragraphs

    def _identify_subparagraphs(self, doc: Document) -> List[Tuple[int, List[int]]]:
        """
        Identify subparagraphs within paragraphs.
        Subparagraphs are complex periods dependent on each other.

        Args:
            doc: python-docx Document object

        Returns:
            List of tuples (paragraph_index, [run_indices])
        """
        subparagraphs = []

        for i, para in enumerate(doc.paragraphs):
            text = para.text
            if not text.strip():
                continue

            # Split by complex sentence markers (;, :, etc.)
            parts = re.split(r'[;:]', text)
            if len(parts) > 1:
                # This paragraph contains subparagraphs
                run_groups = []
                for part_idx in range(len(parts)):
                    run_groups.append(part_idx)
                subparagraphs.append((i, run_groups))

        logger.info(f"Identified {len(subparagraphs)} paragraphs with subparagraphs")
        return subparagraphs

    def _identify_sentences(self, doc: Document) -> List[Tuple[int, List[str]]]:
        """
        Identify sentences in document.
        Sentences start with space + capital letter and end with punctuation.

        Args:
            doc: python-docx Document object

        Returns:
            List of tuples (paragraph_index, [sentences])
        """
        sentence_map = []

        for i, para in enumerate(doc.paragraphs):
            text = para.text
            if not text.strip():
                continue

            # Split into sentences (by period, exclamation, question mark followed by space)
            sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
            sentences = [s.strip() for s in sentences if s.strip()]

            if sentences:
                sentence_map.append((i, sentences))

        total_sentences = sum(len(sents) for _, sents in sentence_map)
        logger.info(f"Identified {total_sentences} sentences across {len(sentence_map)} paragraphs")
        return sentence_map

    def _apply_framing_docx(
        self,
        input_path: str,
        output_path: str,
        framing_options: Dict[str, bool]
    ) -> Dict[str, Any]:
        """
        Apply framing (borders) to DOCX document parts.

        Args:
            input_path: Input file path
            output_path: Output file path
            framing_options: Dictionary with boolean flags

        Returns:
            Result information
        """
        logger.info("Applying framing to DOCX document")

        try:
            doc = Document(input_path)
            borders_applied = 0

            # Apply borders based on options
            if framing_options.get('sections', False):
                sections = self._identify_sections(doc)
                for start_idx, end_idx in sections:
                    for idx in range(start_idx, end_idx + 1):
                        self._add_paragraph_border(doc.paragraphs[idx])
                        borders_applied += 1
                logger.info(f"Applied borders to {len(sections)} sections")

            if framing_options.get('paragraphs', False):
                paragraphs = self._identify_paragraphs(doc)
                for idx in paragraphs:
                    self._add_paragraph_border(doc.paragraphs[idx])
                    borders_applied += 1
                logger.info(f"Applied borders to {len(paragraphs)} paragraphs")

            if framing_options.get('subparagraphs', False):
                subparagraphs = self._identify_subparagraphs(doc)
                # For subparagraphs, we apply borders to the containing paragraph
                for para_idx, _ in subparagraphs:
                    self._add_paragraph_border(doc.paragraphs[para_idx])
                    borders_applied += 1
                logger.info(f"Applied borders to {len(subparagraphs)} subparagraphs")

            if framing_options.get('sentences', False):
                sentence_map = self._identify_sentences(doc)
                logger.debug(f"Sentence map example: {sentence_map[:3]}")
                # For sentences, we need to create separate runs with borders
                # This is complex in DOCX, so we apply borders to paragraphs containing sentences
                for para_idx, sentences in sentence_map:
                    logger.debug(f"Applying sentence borders to paragraph {para_idx} with sentences: {sentences[:3]}")
                    if len(sentences) > 0:
                        self._add_paragraph_border(doc.paragraphs[para_idx])
                        borders_applied += 1
                logger.info(f"Applied borders to paragraphs containing sentences")

            # Save document
            doc.save(output_path)

            logger.info(f"DOCX framing completed: {borders_applied} borders applied")

            return {
                'success': True,
                'output_path': output_path,
                'format': 'docx',
                'borders_applied': borders_applied,
                'framing_options': framing_options
            }

        except Exception as e:
            logger.error(f"DOCX framing error: {str(e)}")
            raise FormattingException(f"DOCX framing failed: {str(e)}")

    def _apply_framing_pdf(
        self,
        input_path: str,
        output_path: str,
        framing_options: Dict[str, bool]
    ) -> Dict[str, Any]:
        """
        Apply framing (borders) to PDF document parts.

        TODO: This is a placeholder for future PDF border implementation.
        PDF border application requires more complex text extraction and positioning.

        Args:
            input_path: Input file path
            output_path: Output file path
            framing_options: Dictionary with boolean flags

        Returns:
            Result information
        """
        logger.info("Applying framing to PDF document (basic implementation)")
        logger.warning("PDF framing support is limited and under development")

        try:
            # Open PDF
            doc = pymupdf.open(input_path)
            output_doc = pymupdf.open()

            borders_applied = 0

            for page in doc:
                # Create new page
                new_page = output_doc.new_page(width=page.rect.width, height=page.rect.height)

                # Copy original content
                new_page.show_pdf_page(new_page.rect, doc, page.number)

                # TODO: Implement text block identification and border drawing
                # This requires:
                # 1. Extract text blocks with positions
                # 2. Identify sections/paragraphs/sentences based on positions and content
                # 3. Draw rectangles around identified blocks

                # Placeholder: Draw border around entire page as example
                if any(framing_options.values()):
                    rect = pymupdf.Rect(50, 50, page.rect.width - 50, page.rect.height - 50)
                    new_page.draw_rect(rect, color=(0, 0, 0), width=0.5)
                    borders_applied += 1

            # Save output
            output_doc.save(output_path)
            output_doc.close()
            doc.close()

            logger.info(f"PDF framing completed: {borders_applied} borders applied (basic)")

            return {
                'success': True,
                'output_path': output_path,
                'format': 'pdf',
                'borders_applied': borders_applied,
                'framing_options': framing_options,
                'note': 'PDF framing is in development - currently applies page-level borders'
            }

        except Exception as e:
            logger.error(f"PDF framing error: {str(e)}")
            raise FormattingException(f"PDF framing failed: {str(e)}")

    def _parse_color(self, color_str: str) -> Optional[tuple]:
        pass

    def get_available_styles(self, file_format: str) -> Dict[str, Any]:
        """
        Get available formatting options for a file format.

        Args:
            file_format: File format (docx, pdf, txt)

        Returns:
            Dictionary with available options
        """
        if file_format not in self.SUPPORTED_FORMATS:
            return {
                'format': file_format,
                'supported': False,
                'options': []
            }

        return {
            'format': file_format,
            'supported': True,
            'options': self.SUPPORTED_FORMATS[file_format],
            'option_details': {
                'font_name': {
                    'type': 'string',
                    'description': 'Font family name',
                    'examples': ['Arial', 'Times New Roman', 'Calibri']
                },
                'font_size': {
                    'type': 'number',
                    'description': 'Font size in points',
                    'examples': [10, 11, 12, 14, 16]
                },
                'font_color': {
                    'type': 'string',
                    'description': 'Font color in hex format',
                    'examples': ['#000000', '#FF0000', '#0000FF']
                },
                'bold': {
                    'type': 'boolean',
                    'description': 'Apply bold formatting'
                },
                'italic': {
                    'type': 'boolean',
                    'description': 'Apply italic formatting'
                },
                'alignment': {
                    'type': 'string',
                    'description': 'Text alignment',
                    'examples': ['left', 'center', 'right', 'justify']
                }
            }
        }


# Singleton instance
_formatting_service_instance: Optional[FormattingService] = None


def get_formatting_service() -> FormattingService:
    """
    Get or create FormattingService singleton instance.

    Returns:
        FormattingService instance (singleton)
    """
    global _formatting_service_instance

    if _formatting_service_instance is None:
        _formatting_service_instance = FormattingService()
        logger.info("Formatting service singleton instance created")

    return _formatting_service_instance
