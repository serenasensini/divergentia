"""
Helper utilities for python-docx XML manipulation
"""
import logging
from typing import Optional, List, Tuple, Dict, Any

from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import RGBColor, Pt

logger = logging.getLogger(__name__)


class DocxXMLHelper:
    """Helper class for python-docx XML manipulation"""
    
    @staticmethod
    def has_complex_field(run) -> bool:
        """
        Check if run contains citation/reference field.
        
        Args:
            run: python-docx run object
            
        Returns:
            True if run contains complex fields (citations, references)
        """
        if run._element is None:
            return False
        
        for child in run._element:
            tag = str(child.tag)
            if any(marker in tag for marker in ['fldChar', 'instrText', 'fldData']):
                return True
        return False
    
    @staticmethod
    def create_border_element(
        border_name: str,
        width: int,
        color: str,
        style: str
    ) -> OxmlElement:
        """
        Create a border XML element.
        
        Args:
            border_name: Border position (top, left, bottom, right, insideH, insideV)
            width: Border width in eighths of a point
            color: Border color in hex format without # (e.g., '000000')
            style: Border style (single, double, dashed, etc.)
            
        Returns:
            OxmlElement for the border
        """
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), style)
        border.set(qn('w:sz'), str(width))
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), color)
        return border
    
    @staticmethod
    def apply_run_formatting(
        run,
        font_name: Optional[str] = None,
        font_size: Optional[int] = None,
        color_rgb: Optional[Tuple[int, int, int]] = None,
        bold: Optional[bool] = None,
        italic: Optional[bool] = None,
        underline: Optional[bool] = None
    ) -> None:
        """
        Apply formatting to a run.
        
        Args:
            run: python-docx run object
            font_name: Font family name (e.g., 'Arial')
            font_size: Font size in points
            color_rgb: RGB color tuple (r, g, b)
            bold: Whether to apply bold
            italic: Whether to apply italic
            underline: Whether to apply underline
        """
        if font_name:
            run.font.name = font_name
        if font_size:
            run.font.size = Pt(font_size)
        if color_rgb:
            run.font.color.rgb = RGBColor(*color_rgb)
        if bold is not None:
            run.bold = bold
        if italic is not None:
            run.italic = italic
        if underline is not None:
            run.underline = underline
    
    @staticmethod
    def extract_run_formatting(run) -> Dict[str, Any]:
        """
        Extract formatting from a run.
        
        Args:
            run: python-docx run object
            
        Returns:
            Dictionary with formatting properties
        """
        return {
            'font_name': run.font.name,
            'font_size': run.font.size,
            'font_color': run.font.color.rgb if run.font.color.rgb else None,
            'bold': run.bold,
            'italic': run.italic,
            'underline': run.underline
        }
    
    @staticmethod
    def set_table_borders(
        table,
        width: int,
        color: str,
        style: str,
        borders: Optional[List[str]] = None
    ) -> None:
        """
        Set borders for a table.
        
        Args:
            table: python-docx table object
            width: Border width in eighths of a point
            color: Border color in hex format without # (e.g., '000000')
            style: Border style (single, double, dashed, etc.)
            borders: List of border names to set (default: all borders)
        """
        if borders is None:
            borders = ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']
        
        tbl = table._element
        tblPr = tbl.find(qn('w:tblPr'))
        if tblPr is None:
            tblPr = OxmlElement('w:tblPr')
            tbl.insert(0, tblPr)
        
        # Remove existing borders
        existing = tblPr.find(qn('w:tblBorders'))
        if existing is not None:
            tblPr.remove(existing)
        
        # Create new borders
        tblBorders = OxmlElement('w:tblBorders')
        for border_name in borders:
            border = DocxXMLHelper.create_border_element(border_name, width, color, style)
            tblBorders.append(border)
        
        tblPr.append(tblBorders)
    
    @staticmethod
    def copy_run_to_paragraph(source_run, target_paragraph):
        """
        Copy a run to a target paragraph, preserving all formatting and content.
        
        Args:
            source_run: Source run to copy from
            target_paragraph: Target paragraph to add run to
            
        Returns:
            The newly created run in target paragraph
        """
        new_run = target_paragraph.add_run(source_run.text)
        
        # Copy formatting
        formatting = DocxXMLHelper.extract_run_formatting(source_run)
        DocxXMLHelper.apply_run_formatting(
            new_run,
            font_name=formatting.get('font_name'),
            font_size=formatting.get('font_size').pt if formatting.get('font_size') else None,
            color_rgb=formatting.get('font_color'),
            bold=formatting.get('bold'),
            italic=formatting.get('italic'),
            underline=formatting.get('underline')
        )
        
        return new_run

