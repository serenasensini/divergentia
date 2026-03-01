"""
Document Formatting Service - Handle document style modifications
"""
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
# import pymupdf  # PyMuPDF

from app.exceptions.custom_exceptions import (
    FormattingException,
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
                logger.debug(f"Framing options received: {framing_options}")
                return self._apply_framing_docx(input_path, output_path, framing_options)
            elif file_extension == 'pdf':
                return "PDF framing is currently under development and has limited support"
                # return self._apply_framing_pdf(input_path, output_path, framing_options)
            else:
                raise FormattingException(f"Framing not supported for {file_extension}")

        except Exception as e:
            logger.error(f"Framing error: {str(e)}")
            raise FormattingException(f"Failed to apply framing: {str(e)}")

    def apply_spacing(
        self,
        input_path: str,
        output_path: str,
        spacing_options: Dict[str, bool]
    ) -> Dict[str, Any]:
        """
        Apply spacing to document parts.

        Args:
            input_path: Path to input document
            output_path: Path to save framed document
            spacing_options: Dictionary with boolean flags for each document part

        Returns:
            Dictionary with result information

        Raises:
            FormattingException: If framing fails
        """
        logger.info(f"Applying spacing to {input_path}")

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
                logger.debug(f"Spacing options received: {spacing_options}")
                return self._apply_spacing_docx(input_path, output_path, spacing_options)
            elif file_extension == 'pdf':
                return "PDF spacing is currently under development and has limited support"
                # return self._apply_framing_pdf(input_path, output_path, framing_options)
            else:
                raise FormattingException(f"Framing not supported for {file_extension}")

        except Exception as e:
            logger.error(f"Framing error: {str(e)}")
            raise FormattingException(f"Failed to apply framing: {str(e)}")

    def apply_keywords(
        self,
        input_path: str,
        output_path: str,
        keyword_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract keywords from document sections and add them as initial paragraphs.

        Args:
            input_path: Input file path
            output_path: Output file path
            keyword_options: Dictionary with keyword extraction options

        Returns:
            Result information including number of sections processed
        """
        logger.info(f"Applying keyword extraction to {input_path}")

        # Determine file type
        file_extension = Path(input_path).suffix.lower().lstrip('.')

        if file_extension not in self.SUPPORTED_FORMATS:
            raise FormattingException(
                f"Unsupported file format: {file_extension}",
                payload={'supported_formats': list(self.SUPPORTED_FORMATS.keys())}
            )

        # Apply keywords based on file type
        try:
            if file_extension == 'docx':
                logger.debug(f"Keyword options received: {keyword_options}")
                return self._apply_keywords_docx(input_path, output_path, keyword_options)
            elif file_extension == 'pdf':
                raise FormattingException("PDF keyword extraction is not currently supported")
            else:
                raise FormattingException(f"Keyword extraction not supported for {file_extension}")

        except Exception as e:
            logger.error(f"Keyword extraction error: {str(e)}")
            raise FormattingException(f"Failed to apply keyword extraction: {str(e)}")

    def apply_highlighting(
        self,
        input_path: str,
        output_path: str,
        highlighting_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply part-of-speech text formatting to document text.

        Args:
            input_path: Input file path
            output_path: Output file path
            highlighting_options: Dictionary with text formatting options
                - enabled: bool - Enable text formatting
                - color: str - Text color in hex format (e.g., "#FF0000")
                - style: str - Text styles: 'bold', 'italic', 'underline', or combinations like 'bold,italic'
                - font_size: int - Font size in points (6-72)
                - font_family: str - Font family name (e.g., 'Times New Roman', 'Arial', 'Courier New')
                - nouns: bool - Format nouns
                - verbs: bool - Format verbs
                - adjectives: bool - Format adjectives
                - adverbs: bool - Format adverbs

        Returns:
            Result information including number of words formatted
        """
        logger.info(f"Applying part-of-speech text formatting to {input_path}")

        # Determine file type
        file_extension = Path(input_path).suffix.lower().lstrip('.')

        if file_extension not in self.SUPPORTED_FORMATS:
            raise FormattingException(
                f"Unsupported file format: {file_extension}",
                payload={'supported_formats': list(self.SUPPORTED_FORMATS.keys())}
            )

        # Check if highlighting is enabled
        if not highlighting_options.get('enabled', False):
            raise FormattingException("Text formatting is not enabled in the provided options")

        # Validate at least one POS is selected
        pos_selected = any([
            highlighting_options.get('nouns', False),
            highlighting_options.get('verbs', False),
            highlighting_options.get('adjectives', False),
            highlighting_options.get('adverbs', False)
        ])

        if not pos_selected:
            raise FormattingException("At least one part of speech must be selected for text formatting")

        # Apply highlighting based on file type
        try:
            if file_extension == 'docx':
                logger.debug(f"Text formatting options received: {highlighting_options}")
                return self._apply_highlighting_docx(input_path, output_path, highlighting_options)
            elif file_extension == 'pdf':
                raise FormattingException("PDF text formatting is not currently supported")
            else:
                raise FormattingException(f"Text formatting not supported for {file_extension}")

        except Exception as e:
            logger.error(f"Text formatting error: {str(e)}")
            raise FormattingException(f"Failed to apply text formatting: {str(e)}")

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

            Example options:
            {
            "formatting": {
                "titles": false,
                "paragraphs": false,
                "paragraphs_titles": false,
                "captions": false,
                "bibliography": false,
                "theme": {
                  "red_green": {
                    "positive": "#00FF00",
                    "negative": "#FF0000"
                  },
                  "blue_orange": {
                    "positive": "#FFA500",
                    "negative": "#0000FF"
                  },
                  "purple_yellow": {
                    "positive": "#FFFF00",
                    "negative": "#800080"
                  }
                }
            }
        }

        Returns:
            Result information
        """
        logger.info("Formatting DOCX document")

        try:
            doc = Document(input_path)
            paragraphs_modified = 0

            # Apply formatting based on specific options (e.g. only to titles, paragraphs, etc.)
            logger.debug(f"Options received for formatting: {options}")

            theme = options.get('theme')
            logger.debug(f"Received theme option: {theme}")
            primary_col = theme.get('positive') if theme else None
            secondary_col = theme.get('negative') if theme else None
            logger.debug(f"Primary color: {primary_col}, Secondary color: {secondary_col}")

            colors = [primary_col, secondary_col]

            # Map options to their corresponding identification methods
            formatting_tasks = [
                ('titles', self._identify_main_title, 'main titles'),
                ('paragraphs', self._identify_paragraphs, 'paragraphs'),
                ('paragraphs_titles', self._identify_section_titles, 'section titles'),
                ('captions', self._identify_image_captions, 'image captions')
            ]

            for option_key, identify_method, label in formatting_tasks:
                if options.get(option_key):
                    indices = identify_method(doc)
                    logger.debug(f"Found {label}: {indices}")
                    # Apply theme-based formatting according to the specified theme
                    self._apply_color_to_indices(doc, indices, colors, label)

            if options.get('captions'):
                pass
            if options.get('bibliography'):
                pass

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
        # logger.info("Formatting PDF document")
        # logger.warning("PDF formatting has limited support")
        #
        # try:
        #     # Open PDF
        #     doc = pymupdf.open(input_path)
        #     pages_processed = 0
        #
        #     # Extract formatting options
        #     font_name = options.get('font_name', 'helv')
        #     font_size = options.get('font_size', 11)
        #     font_color = options.get('font_color', '#000000')
        #
        #     # Parse color
        #     color_rgb = self._parse_color(font_color)
        #     color_tuple = tuple(c / 255.0 for c in color_rgb) if color_rgb else (0, 0, 0)
        #
        #     # Create new PDF with styling
        #     output_doc = pymupdf.open()
        #
        #     for page in doc:
        #         # Extract text
        #         text = page.get_text()
        #
        #         # Create new page
        #         new_page = output_doc.new_page(width=page.rect.width, height=page.rect.height)
        #
        #         # Insert text with new formatting
        #         rect = pymupdf.Rect(50, 50, page.rect.width - 50, page.rect.height - 50)
        #         new_page.insert_textbox(
        #             rect,
        #             text,
        #             fontsize=float(font_size),
        #             fontname=font_name,
        #             color=color_tuple
        #         )
        #
        #         pages_processed += 1
        #
        #     # Save output
        #     output_doc.save(output_path)
        #     output_doc.close()
        #     doc.close()
        #
        #     logger.info(f"PDF formatting completed: {pages_processed} pages processed")
        #
        #     return {
        #         'success': True,
        #         'output_path': output_path,
        #         'format': 'pdf',
        #         'pages_processed': pages_processed,
        #         'applied_options': options,
        #         'note': 'PDF formatting support is limited'
        #     }
        #
        # except Exception as e:
        #     # logger.error(f"PDF formatting error: {str(e)}")
        #     raise FormattingException(f"PDF formatting failed: {str(e)}")


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
            logger.debug(f"Parsed color {color_str} to RGB: ({r}, {g}, {b})")
            return (r, g, b)

        except (ValueError, IndexError) as e:
            logger.warning(f"Invalid color format: {color_str}")
            return None

    def _apply_color_to_indices(
        self,
        doc: Document,
        indices: List[int],
        colors: List[str],
        label: str
    ) -> None:
        """
        Apply color to paragraph runs at specified indices.

        Args:
            doc: python-docx Document object
            indices: List of paragraph indices to color
            colors: List of available colors (will pop from front)
            label: Label for logging purposes
        """
        if not colors:
            logger.warning(f"No colors available for {label}")
            return

        color = colors.pop(0)
        if color:
            color_rgb = self._parse_color(color)
            logger.debug(f"Parsed color RGB for {label}: {color_rgb}")
            if color_rgb:
                for idx in indices:
                    for run in doc.paragraphs[idx].runs:
                        run.font.color.rgb = RGBColor(*color_rgb)
        logger.debug(f"Remaining colors after processing {label}: {colors}")

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

    # FIXME: funziona con i paragrafi ma non con le frasi, da capire se è un problema di identificazione o di applicazione del bordo
    def _add_sentence_border(self, sentence) -> None:
        """
        Add border to a sentence.

        Args:
            paragraph: python-docx paragraph object
        """
        pPr = sentence._element.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')

        for border_name in ['top', 'left', 'bottom', 'right']:
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), self.DEFAULT_BORDER_STYLE)
            border.set(qn('w:sz'), str(self.DEFAULT_BORDER_WIDTH))
            border.set(qn('w:space'), '1')
            border.set(qn('w:color'), self.DEFAULT_BORDER_COLOR)
            pBdr.append(border)

        pPr.append(pBdr)


    def _add_paragraph_spacing(self, paragraph) -> None:
        """
        Add a new line before and after a paragraph.

        Args:
            paragraph: python-docx paragraph object
        """
        # Add a new line before the input paragraph
        p = paragraph._element
        # Add <w:br/> before the paragraph
        p.addprevious(OxmlElement('w:br'))
        # Add <w:br/> after the paragraph
        p.addnext(OxmlElement('w:br'))

    def _add_sentence_spacing(self, paragraph) -> None:
        """
        Add spacing between sentences in a paragraph using spaCy Sentencizer.

        This method uses spaCy's Sentencizer for accurate sentence boundary detection,
        which properly handles abbreviations, complex punctuation, and language-specific rules.

        Args:
            paragraph: python-docx paragraph object
        """
        from app.services.keyword_service import get_keyword_service

        text = paragraph.text
        logger.debug(f"Adding sentence spacing to paragraph: '{text[:50]}...'")

        if not text.strip():
            return

        # Use spaCy Sentencizer for accurate sentence splitting
        keyword_service = get_keyword_service()
        sentences = keyword_service.split_sentences(text)

        logger.debug(f"Identified {len(sentences)} sentences for spacing")

        if len(sentences) <= 1:
            logger.debug("Only one sentence found, no spacing needed")
            return  # No need to add breaks if there's only one sentence

        # Clear existing runs while preserving paragraph properties
        for run in paragraph.runs:
            r = run._element
            r.getparent().remove(r)

        # Re-add sentences with line breaks between them
        for i, sentence in enumerate(sentences):
            logger.debug(f"Adding sentence {i+1}/{len(sentences)}: '{sentence[:30]}...'")
            paragraph.add_run(sentence)

            # Add line break after each sentence except the last one
            if i < len(sentences) - 1:
                paragraph.add_run().add_break()
                paragraph.add_run().add_break()

        logger.debug(f"Finished adding sentence spacing to paragraph")


    def _identify_sections(self, doc: Document) -> List[Tuple[int, int, str]]:
        """
        Identifica sezioni nel documento. Una sezione è il testo che si trova tra due headings
        (o dopo un heading fino alla fine del documento).

        Un heading è identificato da:
        - Stile "Heading" (qualsiasi livello)
        - Font size >= 14.0 pt

        Args:
            doc: python-docx Document object

        Returns:
            Lista di tuple (start_index, end_index, section_text) dove:
            - start_index: indice del primo paragrafo della sezione
            - end_index: indice dell'ultimo paragrafo della sezione (prima del prossimo heading)
            - section_text: testo completo della sezione
        """
        sections = []
        current_section_start = None
        current_section_paragraphs = []

        logger.info('Identifying sections')
        logger.debug(f"Total paragraphs in document: {len(doc.paragraphs)}")

        try:
            for i in range(len(doc.paragraphs)):
                para = doc.paragraphs[i]
                text = para.text.strip()

                if not text:
                    # Paragrafo vuoto: se siamo in una sezione, lo aggiungiamo
                    if current_section_start is not None:
                        current_section_paragraphs.append(para.text)
                    continue

                logger.debug(f"Analyzing paragraph {i}: '{text[:50]}...'")

                # Determina se questo paragrafo è un heading
                style_name = para.style.name
                is_heading = 'Heading' in style_name

                # Controlla anche il font size se disponibile
                font_size = None
                try:
                    if para.style.font.size:
                        font_size = para.style.font.size.pt
                except:
                    # Se non c'è font size nello stile, proviamo nei run
                    if para.runs:
                        for run in para.runs:
                            if run.font.size:
                                font_size = run.font.size.pt
                                break

                is_large_font = font_size is not None and font_size >= 14.0

                logger.debug(f"  Style: {style_name}, is_heading: {is_heading}, font_size: {font_size}, is_large_font: {is_large_font}")

                # Un heading delimita le sezioni
                if is_heading or is_large_font:
                    logger.debug(f"  Found heading/delimiter at paragraph {i}")

                    # Se c'era una sezione in corso, la chiudiamo
                    if current_section_start is not None and current_section_paragraphs:
                        section_text = '\n'.join(current_section_paragraphs)
                        sections.append((current_section_start, i - 1, section_text))
                        logger.debug(f"  Closed section: start={current_section_start}, end={i-1}, text_length={len(section_text)}")

                    # Reset per eventuale nuova sezione
                    current_section_start = None
                    current_section_paragraphs = []
                else:
                    # Questo è testo normale: fa parte di una sezione
                    if current_section_start is None:
                        # Inizia una nuova sezione
                        current_section_start = i
                        logger.debug(f"  Started new section at paragraph {i}")

                    current_section_paragraphs.append(para.text)

            # Chiudi l'ultima sezione se presente
            if current_section_start is not None and current_section_paragraphs:
                section_text = '\n'.join(current_section_paragraphs)
                sections.append((current_section_start, len(doc.paragraphs) - 1, section_text))
                logger.debug(f"Closed final section: start={current_section_start}, end={len(doc.paragraphs)-1}, text_length={len(section_text)}")

            logger.info(f"Identified {len(sections)} sections")
            for idx, (start, end, text) in enumerate(sections):
                logger.debug(f"Section {idx}: paragraphs {start}-{end}, text preview: '{text[:100]}...'")

        except Exception as e:
            logger.error(f"Error identifying sections: {str(e)}", exc_info=True)

        return sections

    def _identify_paragraphs(self, doc: Document) -> List[int]:
        """
        Identify paragraphs in document.
        A paragraph is text that follows a heading (Heading 2, 3, etc.) and ends before the next heading.

        Args:
            doc: python-docx Document object

        Returns:
            List of paragraph indices that are part of content sections (not headings)
        """
        paragraphs = []
        in_paragraph_section = False

        for i, para in enumerate(doc.paragraphs):
            style_name = para.style.name

            # Check if this is a section heading (Heading 2, 3, 4, etc. but not Heading 1)
            is_section_heading = 'Heading' in style_name and 'Heading 1' not in style_name

            if is_section_heading:
                # We found a section heading, the next paragraphs will be part of this section
                in_paragraph_section = True
                logger.debug(f"Found section heading at index {i}: '{para.text[:30]}...'")
                continue

            # Check if this is a main title (Heading 1) - this ends the current paragraph section
            if 'Heading 1' in style_name:
                in_paragraph_section = False
                logger.debug(f"Found main title at index {i}, ending paragraph section")
                continue

            # If we're in a paragraph section and this is non-empty text, it's a paragraph
            if in_paragraph_section and para.text.strip():
                logger.debug(f"Identified paragraph {i}: '{para.text[:30]}...'")
                paragraphs.append(i)

        logger.info(f"Identified {len(paragraphs)} paragraphs (text following section headings)")
        if paragraphs:
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
        Identify sentences in document using spaCy's Sentencizer.

        This method uses spaCy's Sentencizer for accurate sentence boundary detection,
        which handles:
        - Abbreviations (e.g., "Dr.", "etc.", "es.")
        - Complex punctuation (quotes, parentheses)
        - Multiple languages
        - Edge cases that regex patterns miss

        Args:
            doc: python-docx Document object

        Returns:
            List of tuples (paragraph_index, [sentences])
            where each tuple contains the paragraph index and a list of sentence strings
        """
        from app.services.keyword_service import get_keyword_service

        sentence_map = []
        keyword_service = get_keyword_service()

        for i, para in enumerate(doc.paragraphs):
            # Skip headings as they're typically not sentence content
            if 'Heading' in para.style.name:
                logger.debug(f"Skipping sentence identification for paragraph {i} (Heading style)")
                continue

            text = para.text
            if not text.strip():
                continue

            logger.debug(f"Analyzing paragraph {i} for sentences: '{text[:50]}...'")

            # Use spaCy Sentencizer for accurate sentence splitting
            sentences = keyword_service.split_sentences(text)

            if sentences:
                logger.debug(f"Identified {len(sentences)} sentences in paragraph {i}")
                logger.debug(f"  First sentence: '{sentences[0][:50]}...'")
                sentence_map.append((i, sentences))

        total_sentences = sum(len(sents) for _, sents in sentence_map)
        logger.info(f"Identified {total_sentences} sentences across {len(sentence_map)} paragraphs using spaCy Sentencizer")

        return sentence_map

    # Identify main title (Heading 1) - this is a special case for framing main title only
    def _identify_main_title(self, doc: Document) -> List[int]:
        """
        Identify main title in document.
        Titles are paragraphs with specific styles (e.g. Heading 1) or formatting.

        Args:
            doc: python-docx Document object

        Returns:
            List of paragraph indices that are identified as titles
        """
        title_indices = []

        for i, para in enumerate(doc.paragraphs):
            style_name = para.style.name
            logger.debug(f"Analyzing paragraph {i} for main title: style='{style_name}', text='{para.text[:30]}...'")
            if 'Heading 1' in style_name:
                title_indices.append(i)

        logger.info(f"Identified {len(title_indices)} titles")
        logger.debug(f"Identified title indices: {title_indices}")
        return title_indices

    # Identify section titles (Heading 2, Heading 3) - this is a special case for framing section titles only
    def _identify_section_titles(self, doc: Document) -> List[int]:
        """
        Identify titles in document.
        Titles are paragraphs with specific styles (e.g. Heading 2, Heading 3) or formatting.

        Args:
            doc: python-docx Document object

        Returns:
            List of paragraph indices that are identified as titles
        """
        title_indices = []

        for i, para in enumerate(doc.paragraphs):
            style_name = para.style.name
            if 'Heading' in style_name and 'Heading 1' not in style_name:
                title_indices.append(i)

        logger.info(f"Identified {len(title_indices)} titles")
        return title_indices

    # Identify captions - this is a special case for image captions
    def _identify_image_captions(self, doc: Document) -> List[int]:
        """
        Identify image captions in document.
        Captions are paragraphs that follow an image and have specific styles or formatting.

        Args:
            doc: python-docx Document object
        Returns:
            List of paragraph indices that are identified as image captions
        """
        caption_indices = []
        for i in range(1, len(doc.paragraphs)):
            prev_para = doc.paragraphs[i - 1]
            current_para = doc.paragraphs[i]

            # Check if previous paragraph contains an image
            has_image = any(run.element.xpath('.//w:drawing') for run in prev_para.runs)

            # Check if current paragraph is styled as a caption (e.g. "Caption" style)
            is_caption_style = 'Caption' in current_para.style.name

            if has_image and is_caption_style:
                caption_indices.append(i)
        logger.info(f"Identified {len(caption_indices)} image captions")
        logger.debug(f"Identified caption indices: {caption_indices}")
        return caption_indices

    def _apply_spacing_docx(
        self,
        input_path: str,
        output_path: str,
        spacing_options: Dict[str, bool]
    ) -> Dict[str, Any]:
        """
        Apply spacing to DOCX document parts.

        Args:
            input_path: Input file path
            output_path: Output file path
            spacing_options: Dictionary with boolean flags

        Returns:
            Result information
        """
        logger.info("Applying spacing to DOCX document")

        try:
            doc = Document(input_path)
            spacing_applied = 0

            # Apply spacing based on options
            if spacing_options.get('paragraphs', False):
                logging.debug(f"Identifying PARAGRAPHS for spacing application")
                paragraphs = self._identify_paragraphs(doc)
                for idx in paragraphs:
                    logger.debug(f"Applying spacing to paragraph {idx}: '{doc.paragraphs[idx].text[:30]}...'")
                    self._add_paragraph_spacing(doc.paragraphs[idx])
                    spacing_applied += 1
                logger.info(f"Applied spacing to {len(paragraphs)} paragraphs")

            if spacing_options.get('sentences', False):
                logger.debug(f"Identifying SENTENCES for spacing application")
                sentences_to_process = self._identify_sentences(doc)
                logger.debug(f"Sentences identified for spacing: {sentences_to_process[:3]} (showing first 3)")
                # Process in reversed order to avoid index issues when modifying paragraphs
                for para_idx, sentences in reversed(sentences_to_process):
                    logger.debug(f"Applying sentence spacing to paragraph {para_idx} with sentences: {sentences[:3]} (showing first 3)")
                    self._add_sentence_spacing(doc.paragraphs[para_idx])
                    spacing_applied += 1
                logger.info(f"Applied spacing to sentences in {len(sentences_to_process)} paragraphs")

            # Save document
            doc.save(output_path)
            logger.info(f"DOCX spacing completed: {spacing_applied} spacings applied")

            return {
                'success': True,
                'output_path': output_path,
                'format': 'docx',
                'spacing_applied': spacing_applied,
                'spacing_options': spacing_options
            }

        except Exception as e:
            logger.error(f"DOCX spacing error: {str(e)}")
            raise FormattingException(f"DOCX spacing failed: {str(e)}")

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
            # Apply borders to sections, paragraphs, subparagraphs, sentences based on options
            doc = Document(input_path)
            borders_applied = 0

            # Apply borders based on options
            if framing_options.get('sections', False):
                sections = self._identify_sections(doc)
                logger.debug(f"Total sections identified: {len(sections)}")
                logger.debug(f"Example of identified sections: {[(s[0], s[1]) for s in sections[:3]]}")
                for start_idx, end_idx, section_text in sections:
                    logger.debug("Applying border to section from paragraph index {} to {}".format(start_idx, end_idx))
                    for idx in range(start_idx, end_idx + 1):
                        logger.debug(f"Applying border to paragraph {idx}: '{doc.paragraphs[idx].text[:50]}...'")
                        self._add_paragraph_border(doc.paragraphs[idx])
                        borders_applied += 1
                logger.info(f"Applied borders to {len(sections)} sections")

            if framing_options.get('paragraphs', False):
                paragraphs = self._identify_paragraphs(doc)
                for idx in paragraphs:
                    logger.debug(f"Applying border to paragraph {idx}: '{doc.paragraphs[idx].text}...'")
                    self._add_sentence_border(doc.paragraphs[idx])
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
                # Apply border to each sentence
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
        # logger.info("Applying framing to PDF document (basic implementation)")
        # logger.warning("PDF framing support is limited and under development")
        #
        # try:
        #     # Open PDF
        #     doc = pymupdf.open(input_path)
        #     output_doc = pymupdf.open()
        #
        #     borders_applied = 0
        #
        #     for page in doc:
        #         # Create new page
        #         new_page = output_doc.new_page(width=page.rect.width, height=page.rect.height)
        #
        #         # Copy original content
        #         new_page.show_pdf_page(new_page.rect, doc, page.number)
        #
        #         # TODO: Implement text block identification and border drawing
        #         # This requires:
        #         # 1. Extract text blocks with positions
        #         # 2. Identify sections/paragraphs/sentences based on positions and content
        #         # 3. Draw rectangles around identified blocks
        #
        #         # Placeholder: Draw border around entire page as example
        #         if any(framing_options.values()):
        #             rect = pymupdf.Rect(50, 50, page.rect.width - 50, page.rect.height - 50)
        #             new_page.draw_rect(rect, color=(0, 0, 0), width=0.5)
        #             borders_applied += 1
        #
        #     # Save output
        #     output_doc.save(output_path)
        #     output_doc.close()
        #     doc.close()
        #
        #     logger.info(f"PDF framing completed: {borders_applied} borders applied (basic)")
        #
        #     return {
        #         'success': True,
        #         'output_path': output_path,
        #         'format': 'pdf',
        #         'borders_applied': borders_applied,
        #         'framing_options': framing_options,
        #         'note': 'PDF framing is in development - currently applies page-level borders'
        #     }
        #
        # except Exception as e:
        #     logger.error(f"PDF framing error: {str(e)}")
        #     raise FormattingException(f"PDF framing failed: {str(e)}")
        pass

    def _apply_keywords_docx(
        self,
        input_path: str,
        output_path: str,
        keyword_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Estrae parole chiave dalle sezioni di un documento DOCX e le inserisce come paragrafi formattati.

        Questa funzione analizza un documento DOCX per identificare le sezioni strutturali
        (tramite _identify_sections) e per ciascuna estrae le parole chiave più rilevanti
        utilizzando Ollama come metodo principale, con fallback automatico a spaCy in caso
        di indisponibilità del servizio o errori.

        Flusso di esecuzione:
        1. Caricamento del documento DOCX
        2. Identificazione delle sezioni tramite _identify_sections() che rileva:
           - Pattern di testo (es. " A.", " B.")
           - Stili Heading (Heading 2, 3, etc.)
           - Formattazione speciale (grassetto + font > 11pt)
        3. Per ogni sezione identificata:
           a. Estrazione del testo combinato di tutti i paragrafi della sezione
           b. Tentativo di estrazione keywords con Ollama (metodo principale)
           c. In caso di fallimento, utilizzo di spaCy come fallback
           d. Formattazione delle keywords: "Parole chiave: keyword1, keyword2, ..."
           e. Inserimento come nuovo paragrafo formattato dopo il titolo della sezione
        4. Salvataggio del documento modificato
        5. Restituzione metadati completi sull'operazione

        Formattazione delle keywords inserite:
        - Stile: Italico
        - Dimensione font: 10pt (20 half-points in OpenXML)
        - Posizione: Subito dopo il titolo della sezione
        - Formato testo: "Parole chiave: parola1, parola2, parola3"

        Gestione errori e fallback:
        - Se Ollama non è disponibile: usa spaCy per tutte le sezioni
        - Se Ollama fallisce per una sezione specifica: usa spaCy per quella sezione
        - Se nessuna sezione è identificata: salva documento invariato e restituisce warning
        - Ogni errore viene loggato con dettagli per debugging

        Args:
            input_path (str): Percorso assoluto del file DOCX di input
            output_path (str): Percorso assoluto dove salvare il file DOCX processato
            keyword_options (Dict[str, Any]): Dizionario con opzioni di estrazione:
                - max_keywords (int): Numero di parole chiave per sezione (range: 1-10).
                                     Default: 5
                - include_proper_nouns (bool): Include nomi propri nell'estrazione
                                               (utilizzato solo dal fallback spaCy).
                                               Default: True
                - model (str, optional): Nome del modello Ollama specifico da utilizzare
                                        (es. 'llama2', 'mistral', 'phi').
                                        Se omesso, usa il modello di default configurato.
                                        Default: None

        Returns:
            Dict[str, Any]: Dizionario con informazioni dettagliate sul risultato:
                {
                    'success': bool,                    # True se operazione completata
                    'output_path': str,                 # Path del file generato
                    'format': str,                      # Formato documento ('docx')
                    'sections_processed': int,          # Numero di sezioni processate
                    'total_keywords': int,              # Totale keywords estratte
                    'keyword_options': Dict[str, Any],  # Opzioni utilizzate
                    'extraction_method': str,           # Metodo usato: 'Ollama', 'spaCy',
                                                       # o 'Ollama with spaCy fallback'
                    'ollama_used': bool,               # True se Ollama è stato usato
                    'spacy_fallback_used': bool        # True se fallback è stato attivato
                }

                In caso di nessuna sezione trovata, include anche:
                    'note': str                        # Messaggio descrittivo

        Raises:
            FormattingException: Se si verifica un errore durante:
                - Caricamento del documento
                - Elaborazione delle sezioni
                - Salvataggio del file
                - Qualsiasi altro errore di processing
        """
        logger.info("Applying keyword extraction to DOCX document")

        try:
            from app.services.keyword_service import get_keyword_service
            from app.services.ollama_service import get_ollama_service

            # Load document
            doc = Document(input_path)

            # Get options
            max_keywords = keyword_options.get('max_keywords', 5)
            include_proper_nouns = keyword_options.get('include_proper_nouns', True)
            ollama_model = keyword_options.get('model', None)

            sections_processed = 0
            total_keywords_extracted = 0
            ollama_used = False
            spacy_fallback_used = False

            # Identify sections using the advanced method
            sections = self._identify_sections(doc)
            logger.info(f"Identified {len(sections)} sections for keyword extraction")

            if not sections:
                logger.warning("No sections identified in document")
                doc.save(output_path)
                return {
                    'success': True,
                    'output_path': output_path,
                    'format': 'docx',
                    'sections_processed': 0,
                    'total_keywords': 0,
                    'keyword_options': keyword_options,
                    'note': 'No sections found in document'
                }

            # Try to get Ollama service
            ollama_service = None
            try:
                ollama_service = get_ollama_service()
                use_ollama = True
                logger.info("Ollama service available, will use for keyword extraction")
            except Exception as e:
                use_ollama = False
                logger.warning(f"Ollama service not available: {str(e)}. Will use spaCy fallback")

            # Get spaCy service as fallback
            keyword_service = get_keyword_service()

            logger.debug("Starting section processing loop")
            logger.debug("#################################")
            logger.debug(f"Sections to process: {len(sections)}")
            logger.debug(f"Sections identified: {[(s[0], s[1]) for s in sections]}")
            logger.debug("#################################")

            # IMPORTANTE: Process sections in REVERSE order to avoid index shift problems
            # When we insert a paragraph before a section, all subsequent paragraph indices shift by +1
            # By processing from the last section to the first, we ensure that:
            # - Inserting keywords in section N doesn't affect the indices of sections 0..N-1
            # - The indices remain valid throughout the entire processing loop
            logger.info(f"Processing {len(sections)} sections in REVERSE order to preserve paragraph indices")

            # Process each section (in reverse order)
            for section_num, (start_idx, end_idx, section_text) in enumerate(reversed(sections), 1):
                actual_section_num = len(sections) - section_num + 1  # For logging
                logger.debug(f"Processing section {actual_section_num}/{len(sections)}: paragraphs {start_idx}-{end_idx}")

                # Get the first paragraph of the section to use as title for logging
                first_para = doc.paragraphs[start_idx].text
                logger.debug(f"Section starts with: '{first_para[:50]}...'")

                if not section_text.strip():
                    logger.debug(f"Section {start_idx}-{end_idx} has no text, skipping")
                    continue

                # Extract keywords using Ollama or spaCy
                keywords = []

                if use_ollama:
                    try:
                        keywords = ollama_service.extract_keywords(
                            text=section_text,
                            max_keywords=max_keywords,
                            model=ollama_model,
                            use_cache=True
                        )
                        ollama_used = True
                        logger.debug(f"Ollama extracted keywords: {keywords}")
                    except Exception as e:
                        logger.warning(f"Ollama keyword extraction failed: {str(e)}. Falling back to spaCy")
                        use_ollama = False  # Disable for remaining sections

                # Fallback to spaCy if Ollama failed or not available
                if not keywords:
                    keywords = keyword_service.extract_keywords(
                        text=section_text,
                        max_keywords=max_keywords,
                        include_proper_nouns=include_proper_nouns
                    )
                    spacy_fallback_used = True
                    logger.debug(f"spaCy extracted keywords: {keywords}")

                if keywords:
                    # Format keywords using keyword_service
                    # This returns: "Parole chiave: keyword1, keyword2, keyword3"
                    keyword_text = keyword_service.format_keywords(keywords)
                    logger.debug(f"Formatted keywords for section '{first_para[:30]}...': {keyword_text}")

                    # Insert keyword paragraph right after the section start
                    start_para = doc.paragraphs[start_idx]

                    # Create new paragraph element
                    new_para_element = OxmlElement('w:p')

                    # Create run element with formatting properties
                    run_element = OxmlElement('w:r')

                    # Apply formatting: italic and 10pt font
                    rPr = OxmlElement('w:rPr')
                    italic = OxmlElement('w:i')
                    sz = OxmlElement('w:sz')
                    sz.set(qn('w:val'), '20')  # 10pt = 20 half-points
                    rPr.append(italic)
                    rPr.append(sz)
                    run_element.append(rPr)

                    # Create text element with keyword text
                    text_element = OxmlElement('w:t')
                    text_element.text = keyword_text
                    run_element.append(text_element)

                    # Add run to paragraph
                    new_para_element.append(run_element)

                    # Insert the new paragraph before the section title
                    start_para._element.addprevious(new_para_element)

                    sections_processed += 1
                    total_keywords_extracted += len(keywords)

                    logger.info(f"Added keywords before section '{first_para[:50]}...': {keyword_text}")

            # Save document
            doc.save(output_path)

            # Prepare result metadata
            extraction_method = "Ollama" if ollama_used else "spaCy"
            if ollama_used and spacy_fallback_used:
                extraction_method = "Ollama with spaCy fallback"

            logger.info(f"DOCX keyword extraction completed: {sections_processed} sections processed, "
                       f"{total_keywords_extracted} keywords extracted using {extraction_method}")

            return {
                'success': True,
                'output_path': output_path,
                'format': 'docx',
                'sections_processed': sections_processed,
                'total_keywords': total_keywords_extracted,
                'keyword_options': keyword_options,
                'extraction_method': extraction_method,
                'ollama_used': ollama_used,
                'spacy_fallback_used': spacy_fallback_used
            }

        except Exception as e:
            logger.error(f"DOCX keyword extraction error: {str(e)}")
            raise FormattingException(f"DOCX keyword extraction failed: {str(e)}")

    def _apply_highlighting_docx(
        self,
        input_path: str,
        output_path: str,
        highlighting_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply part-of-speech text formatting to DOCX document.

        This method processes each paragraph in the document, analyzes the text using spaCy
        to identify parts of speech, and applies formatting (color, font, style) based on
        user-specified options.

        Args:
            input_path: Path to input DOCX file
            output_path: Path to save output DOCX file
            highlighting_options: Dictionary containing:
                - enabled: bool - Whether formatting is enabled
                - color: str - Text color in hex format (e.g., "#FF0000")
                - style: str - Text styles: 'bold', 'italic', 'underline', or combinations like 'bold,italic'
                - font_size: int - Font size in points (6-72)
                - font_family: str - Font family name (e.g., 'Times New Roman', 'Arial')
                - nouns: bool - Whether to format nouns
                - verbs: bool - Whether to format verbs
                - adjectives: bool - Whether to format adjectives
                - adverbs: bool - Whether to format adverbs

        Returns:
            Dictionary with result information:
                - success: bool - Whether operation succeeded
                - output_path: str - Path to output file
                - format: str - File format ("docx")
                - words_formatted: int - Total words formatted
                - paragraphs_processed: int - Number of paragraphs processed
                - pos_stats: dict - Statistics per part of speech
                - highlighting_options: dict - Options used

        Raises:
            FormattingException: If document processing fails
        """
        logger.info("Applying part-of-speech text formatting to DOCX document")

        try:
            from app.services.keyword_service import get_keyword_service

            # Load document
            doc = Document(input_path)

            # Get keyword service for POS analysis
            keyword_service = get_keyword_service()

            # Identify sections (this excludes headings)
            sections = self._identify_sections(doc)

            if not sections:
                logger.warning("No sections found in document. Nothing to format.")
                return {
                    'success': True,
                    'output_path': output_path,
                    'format': 'docx',
                    'words_formatted': 0,
                    'paragraphs_processed': 0,
                    'pos_stats': {'nouns': 0, 'verbs': 0, 'adjectives': 0, 'adverbs': 0},
                    'highlighting_options': highlighting_options
                }

            # Extract options
            color = highlighting_options.get('color', '#000000').lstrip('#')
            style_str = highlighting_options.get('style', None)
            font_size = highlighting_options.get('font_size', None)
            font_family = highlighting_options.get('font_family', None)
            highlight_nouns = highlighting_options.get('nouns', False)
            highlight_verbs = highlighting_options.get('verbs', False)
            highlight_adjectives = highlighting_options.get('adjectives', False)
            highlight_adverbs = highlighting_options.get('adverbs', False)

            # Parse styles
            apply_bold = False
            apply_italic = False
            apply_underline = False
            if style_str:
                styles = [s.strip().lower() for s in style_str.split(',')]
                apply_bold = 'bold' in styles
                apply_italic = 'italic' in styles
                apply_underline = 'underline' in styles

            # Convert hex color to RGB
            try:
                r = int(color[0:2], 16)
                g = int(color[2:4], 16)
                b = int(color[4:6], 16)
            except ValueError:
                logger.warning(f"Invalid color format: {color}, using default black")
                r, g, b = 0, 0, 0

            # Statistics
            words_formatted = 0
            paragraphs_processed = 0
            pos_stats = {
                'nouns': 0,
                'verbs': 0,
                'adjectives': 0,
                'adverbs': 0
            }

            logger.info(f"Processing document with color RGB({r}, {g}, {b})")
            logger.info(f"Font settings - Family: {font_family}, Size: {font_size}, Styles: bold={apply_bold}, italic={apply_italic}, underline={apply_underline}")
            logger.info(f"POS to format - Nouns: {highlight_nouns}, Verbs: {highlight_verbs}, "
                       f"Adjectives: {highlight_adjectives}, Adverbs: {highlight_adverbs}")
            logger.info(f"Found {len(sections)} sections to process")

            # Build a set of paragraph indices that are part of sections (not headings)
            section_paragraph_indices = set()
            for start_idx, end_idx, _ in sections:
                for i in range(start_idx, end_idx + 1):
                    section_paragraph_indices.add(i)

            logger.info(f"Processing {len(section_paragraph_indices)} paragraphs (excluding headings)")

            # Process only paragraphs that are part of sections
            for para_idx, paragraph in enumerate(doc.paragraphs):
                # Skip if this paragraph is not part of a section (it's likely a heading)
                if para_idx not in section_paragraph_indices:
                    logger.debug(f"Skipping paragraph {para_idx} (heading or non-section content)")
                    continue

                if not paragraph.text.strip():
                    continue

                paragraphs_processed += 1

                # Analyze text with spaCy
                tokens = keyword_service.analyze_pos(paragraph.text)

                if not tokens:
                    continue

                # Store original formatting
                original_style = paragraph.style
                original_alignment = paragraph.alignment

                # Build a mapping of which tokens to format
                format_map = []
                for token in tokens:
                    should_format = False

                    if token['is_punct'] or token['is_space']:
                        format_map.append(False)
                        continue

                    pos = token['pos']

                    if highlight_nouns and pos in ['NOUN', 'PROPN']:
                        should_format = True
                        pos_stats['nouns'] += 1
                    elif highlight_verbs and pos == 'VERB':
                        should_format = True
                        pos_stats['verbs'] += 1
                    elif highlight_adjectives and pos == 'ADJ':
                        should_format = True
                        pos_stats['adjectives'] += 1
                    elif highlight_adverbs and pos == 'ADV':
                        should_format = True
                        pos_stats['adverbs'] += 1

                    format_map.append(should_format)
                    if should_format:
                        words_formatted += 1

                # Clear existing runs and rebuild with formatting
                for run in paragraph.runs:
                    run._element.getparent().remove(run._element)

                # Reconstruct text with formatting
                for i, token in enumerate(tokens):
                    if token['is_space']:
                        # Skip pure whitespace tokens
                        continue

                    # Create new run
                    run = paragraph.add_run(token['text'])

                    # Apply formatting if needed
                    if i < len(format_map) and format_map[i]:
                        # Apply text color
                        run.font.color.rgb = RGBColor(r, g, b)

                        # Apply font family
                        if font_family:
                            run.font.name = font_family

                        # Apply font size
                        if font_size:
                            run.font.size = Pt(font_size)

                        # Apply text styles
                        if apply_bold:
                            run.bold = True
                        if apply_italic:
                            run.italic = True
                        if apply_underline:
                            run.underline = True

                    # Add space after token if it's not punctuation and not the last token
                    if not token['is_punct'] and i < len(tokens) - 1:
                        next_token = tokens[i + 1] if i + 1 < len(tokens) else None
                        if next_token and not next_token['is_punct']:
                            paragraph.add_run(' ')

                # Restore paragraph formatting
                paragraph.style = original_style
                if original_alignment:
                    paragraph.alignment = original_alignment

            # Save document
            doc.save(output_path)

            logger.info(f"DOCX text formatting completed: {paragraphs_processed} paragraphs processed, "
                       f"{words_formatted} words formatted")
            logger.info(f"POS statistics: {pos_stats}")

            return {
                'success': True,
                'output_path': output_path,
                'format': 'docx',
                'words_formatted': words_formatted,
                'paragraphs_processed': paragraphs_processed,
                'pos_stats': pos_stats,
                'highlighting_options': highlighting_options
            }

        except Exception as e:
            logger.error(f"DOCX text formatting error: {str(e)}")
            raise FormattingException(f"DOCX text formatting failed: {str(e)}")

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
