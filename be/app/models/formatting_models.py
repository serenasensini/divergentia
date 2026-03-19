"""
Data models for document formatting operations
"""
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any


@dataclass
class HighlightingConfig:
    """
    Configuration for text highlighting/formatting.
    
    Attributes:
        color_rgb: RGB color tuple (r, g, b) for text color
        font_family: Optional font family name (e.g., 'Arial', 'Times New Roman')
        font_size: Optional font size in points
        apply_bold: Whether to apply bold formatting
        apply_italic: Whether to apply italic formatting
        apply_underline: Whether to apply underline formatting
        highlight_nouns: Whether to format nouns
        highlight_verbs: Whether to format verbs
        highlight_adjectives: Whether to format adjectives
        highlight_adverbs: Whether to format adverbs
    """
    color_rgb: Tuple[int, int, int]
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    apply_bold: bool = False
    apply_italic: bool = False
    apply_underline: bool = False
    highlight_nouns: bool = False
    highlight_verbs: bool = False
    highlight_adjectives: bool = False
    highlight_adverbs: bool = False

    def should_format_pos(self, pos: str) -> bool:
        """
        Check if a given part-of-speech should be formatted.
        
        Args:
            pos: Part-of-speech tag (e.g., 'NOUN', 'VERB', 'ADJ', 'ADV')
            
        Returns:
            True if this POS should be formatted based on config
        """
        if self.highlight_nouns and pos in ['NOUN', 'PROPN']:
            return True
        elif self.highlight_verbs and pos == 'VERB':
            return True
        elif self.highlight_adjectives and pos == 'ADJ':
            return True
        elif self.highlight_adverbs and pos == 'ADV':
            return True
        return False


@dataclass
class RunInfo:
    """
    Metadata about a document run (text segment with consistent formatting).
    
    Attributes:
        element: Original XML element
        start_pos: Starting character position in paragraph
        end_pos: Ending character position in paragraph
        text: Text content of the run
        has_complex_field: Whether run contains citation/reference field
        original_formatting: Dictionary with original formatting properties
    """
    element: Any
    start_pos: int
    end_pos: int
    text: str
    has_complex_field: bool
    original_formatting: Dict[str, Any]

