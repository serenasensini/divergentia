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

            # Extract formatting options about text styling
            # font_name = options.get('font_name')
            # font_size = options.get('font_size')
            # font_color = options.get('font_color')
            # bold = options.get('bold')
            # italic = options.get('italic')
            # alignment = options.get('alignment')
            #
            # # Apply to all paragraphs
            # for paragraph in doc.paragraphs:
            #     if not paragraph.runs:
            #         continue
            #
            #     # Apply paragraph-level formatting
            #     if alignment:
            #         alignment_map = {
            #             'left': WD_ALIGN_PARAGRAPH.LEFT,
            #             'center': WD_ALIGN_PARAGRAPH.CENTER,
            #             'right': WD_ALIGN_PARAGRAPH.RIGHT,
            #             'justify': WD_ALIGN_PARAGRAPH.JUSTIFY
            #         }
            #         if alignment.lower() in alignment_map:
            #             paragraph.alignment = alignment_map[alignment.lower()]
            #
            #     # Apply run-level formatting
            #     for run in paragraph.runs:
            #         if font_name:
            #             run.font.name = font_name
            #
            #         if font_size:
            #             run.font.size = Pt(int(font_size))
            #
            #         if font_color:
            #             # Parse color (hex format: #RRGGBB)
            #             color = self._parse_color(font_color)
            #             if color:
            #                 run.font.color.rgb = RGBColor(*color)
            #
            #         if bold is not None:
            #             run.font.bold = bool(bold)
            #
            #         if italic is not None:
            #             run.font.italic = bool(italic)
            #
            #     paragraphs_modified += 1

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


    def _add_sentence_spacing(self, sentence) -> None:
        """
        Add spacing to a sentence (implemented as a run).

        Args:
            sentence: python-docx run object representing the sentence
        """
        # Add spacing before the sentence
        sentence.add_break()
        # Add spacing after the sentence
        sentence.add_break()


    def _identify_sections(self, doc: Document) -> List[Tuple[int, int, str]]:
        """
        Identifica sezioni usando multipli criteri:
        - Pattern di testo (es. " A. ")
        - Stili Word applicati
        - Formattazione (grassetto, dimensione font)
        """
        sections = []
        current_section_start = None

        logger.info('Identifying sections')

        logger.debug(f"Total paragraphs in document: {len(doc.paragraphs)}")
        logger.debug("Paragraphs found:", doc.paragraphs)

        try:
            for i in range(len(doc.paragraphs)):
                para = doc.paragraphs[i]
                logger.debug("###############################")
                logger.debug(f"Paragraph {i}: {para.text}")
                text = para.text
                logger.debug(f"Analyzing paragraph {i}: '{text[:30]}...'")
                style_name = para.style.name
                logger.debug(f"Style name: {style_name}")

                # Criterio 1: Pattern di testo esistente
                is_section_by_pattern = re.match(r'^\s+[A-Z]\.', text)
                logger.debug(f"is_section_by_pattern: {is_section_by_pattern}")

                # Criterio 2: Stile Heading
                is_heading = 'Heading' in style_name
                logger.debug(f"is_heading: {is_heading}")

                # Criterio 3: Formattazione grassetto e dimensione
                is_formatted_title = False
                logger.debug(f"is_formatted_title: {is_formatted_title}")
                if para.runs:
                    first_run = para.runs[0]
                    is_formatted_title = (
                            first_run.font.bold and
                            first_run.font.size and
                            first_run.font.size.pt > 11
                    )

                # Determina se è inizio sezione
                if is_section_by_pattern or is_heading or is_formatted_title:
                    logger.debug("Identified section start")
                    if current_section_start is not None:
                        sections.append((current_section_start, i - 1))
                    current_section_start = i

                # Chiudi sezione se termina con punto
                elif current_section_start is not None and text.strip().endswith('.'):
                    if i + 1 >= len(doc.paragraphs) or not doc.paragraphs[i + 1].text.strip():
                        sections.append((current_section_start, i))
                        current_section_start = None

        except Exception as e:
            logger.error(f"Error identifying sections: {str(e)}")

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
        Identify sentences in document.
        Sentences start with space + capital letter and end with punctuation.

        Args:
            doc: python-docx Document object

        Returns:
            List of tuples (paragraph_index, [sentences])
        """
        sentence_map = []

        for i, para in enumerate(doc.paragraphs):
            # If paragraph style is Heading, we skip sentence splitting as it's likely a title
            if 'Heading' in para.style.name:
                logger.debug(f"Skipping sentence identification for paragraph {i} as it is a Heading 1")
                continue
            else:
                text = para.text
                logger.debug(f"Analyzing paragraph {i} for sentences: '{text[:30]}...'")
                if not text.strip():
                    continue

            # Split into sentences (by period, exclamation, question mark followed by space)
            sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
            sentences = [s.strip() for s in sentences if s.strip()]

            if sentences:
                logger.debug(f"Identified sentences in paragraph {i}: {sentences}")
                sentence_map.append((i, sentences))

        total_sentences = sum(len(sents) for _, sents in sentence_map)
        logger.info(f"Identified {total_sentences} sentences across {len(sentence_map)} paragraphs")
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
            # Apply spacing to sections, paragraphs, subparagraphs, sentences based on options
            doc = Document(input_path)
            spacing_applied = 0
            # Apply spacing based on options
            if spacing_options.get('paragraphs', False):
                paragraphs = self._identify_paragraphs(doc)
                for idx in paragraphs:
                    logger.debug(f"Applying spacing to paragraph {idx}: '{doc.paragraphs[idx].text[:30]}...'")
                    self._add_paragraph_spacing(doc.paragraphs[idx])
                    spacing_applied += 1
                logger.info(f"Applied spacing to {len(paragraphs)} paragraphs")
            if spacing_options.get('sentences', False):
                sentence_map = self._identify_sentences(doc)
                for para_idx, sentences in sentence_map:
                    if len(sentences) > 0:
                        logger.debug(f"Applying spacing to paragraph {para_idx} with sentences: {sentences[:30]}...")
                        self._add_paragraph_spacing(doc.paragraphs[para_idx])
                        spacing_applied += 1
                logger.info(f"Applied spacing to paragraphs containing sentences")
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
                for start_idx, end_idx in sections:
                    logger.debug("Applying border to section from paragraph index {} to {}".format(start_idx, end_idx))
                    for idx in range(start_idx, end_idx + 1):
                        logger.debug(f"Applying border to paragraph {idx}: '{doc.paragraphs[idx].text}...'")
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
                        self._add
                        # self._add_paragraph_border(doc.paragraphs[para_idx])
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
        Extract keywords from document sections and add them as initial paragraphs.

        Args:
            input_path: Input file path
            output_path: Output file path
            keyword_options: Dictionary with keyword extraction options

        Returns:
            Result information including number of sections processed
        """
        logger.info("Applying keyword extraction to DOCX document")

        try:
            from app.services.keyword_service import get_keyword_service

            # Load document
            doc = Document(input_path)
            keyword_service = get_keyword_service()

            # Get options
            max_keywords = keyword_options.get('max_keywords', 5)
            include_proper_nouns = keyword_options.get('include_proper_nouns', True)

            sections_processed = 0
            total_keywords_extracted = 0

            # Identify sections and their content
            # A section is defined by a heading (Heading 2, 3, etc.) followed by content paragraphs
            i = 0
            while i < len(doc.paragraphs):
                para = doc.paragraphs[i]
                style_name = para.style.name

                # Check if this is a section heading (Heading 2, 3, 4, etc. but not Heading 1)
                is_section_heading = 'Heading' in style_name and style_name != 'Heading 1'

                if is_section_heading:
                    logger.debug(f"Found section heading at index {i}: '{para.text[:50]}...'")

                    # Collect text from all paragraphs in this section until the next heading
                    section_text = []
                    j = i + 1

                    while j < len(doc.paragraphs):
                        next_para = doc.paragraphs[j]
                        next_style = next_para.style.name

                        # Stop if we hit another heading
                        if 'Heading' in next_style:
                            break

                        # Add paragraph text if not empty
                        if next_para.text.strip():
                            section_text.append(next_para.text)

                        j += 1

                    # Extract keywords from section text
                    if section_text:
                        combined_text = ' '.join(section_text)
                        keywords = keyword_service.extract_keywords(
                            combined_text,
                            max_keywords=max_keywords,
                            include_proper_nouns=include_proper_nouns
                        )

                        if keywords:
                            # Format keywords
                            keyword_text = keyword_service.format_keywords(keywords)
                            logger.debug(f"Extracted keywords for section '{para.text[:30]}...': {keyword_text}")

                            # Insert keyword paragraph right after the heading
                            # We need to insert at position i+1
                            new_para = para._element.addnext(
                                doc.add_paragraph(keyword_text)._element
                            )

                            # Apply italic style to the keyword paragraph
                            keyword_para = doc.paragraphs[i + 1]
                            for run in keyword_para.runs:
                                run.italic = True
                                run.font.size = Pt(10)

                            sections_processed += 1
                            total_keywords_extracted += len(keywords)

                            # Skip the newly inserted paragraph
                            i += 1

                i += 1

            # Save document
            doc.save(output_path)

            logger.info(f"DOCX keyword extraction completed: {sections_processed} sections processed, "
                       f"{total_keywords_extracted} keywords extracted")

            return {
                'success': True,
                'output_path': output_path,
                'format': 'docx',
                'sections_processed': sections_processed,
                'total_keywords': total_keywords_extracted,
                'keyword_options': keyword_options
            }

        except Exception as e:
            logger.error(f"DOCX keyword extraction error: {str(e)}")
            raise FormattingException(f"DOCX keyword extraction failed: {str(e)}")

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
