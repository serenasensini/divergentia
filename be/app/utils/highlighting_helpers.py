"""Helper functions for document highlighting operations"""
import logging
from typing import Dict, Any, Set, Tuple, List
from app.utils.docx_xml_helper import DocxXMLHelper
logger = logging.getLogger(__name__)
def should_skip_paragraph(paragraph) -> Tuple[bool, str]:
    """Determine if paragraph should be skipped during highlighting."""
    if not paragraph.text.strip():
        return (True, "empty paragraph")
    for run in paragraph.runs:
        if DocxXMLHelper.has_complex_field(run):
            return (True, "contains citation/reference fields")
    return (False, "")
