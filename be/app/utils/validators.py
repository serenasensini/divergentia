"""
Input Validation Utilities
"""
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator

from app.exceptions.custom_exceptions import ValidationException


class UploadRequestSchema(BaseModel):
    """Schema for document upload request"""
    # File will be in request.files, this is for validation
    pass


class FramingOptionsSchema(BaseModel):
    """Schema for framing/border options"""
    sections: bool = Field(False, description="Frame each section in one single-cell table")
    paragraphs: bool = Field(False, description="Frame each paragraph in its own single-cell table")
    subparagraphs: bool = Field(False, description="Frame subparagraphs in their own tables")
    sentences: bool = Field(False, description="Frame each sentence in its own single-cell table")
    use_tables: bool = Field(True, description="Use single-cell tables for framing (recommended)")
    border_color: Optional[str] = Field(None, description="Border color in hex format")
    border_style: Optional[str] = Field(None, description="Border style (single, double, dashed, dotted, ...)")
    border_width: Optional[int] = Field(None, ge=1, le=48, description="Border width in eighths of a point (8 = 1pt)")
    cell_margin: Optional[int] = Field(None, ge=0, le=1440, description="Cell inner margin in twips (1/1440 inch)")
    preserve_spacing: bool = Field(True, description="Preserve original paragraph spacing")
    from_original: bool = Field(False, description="Start from the original upload instead of chaining onto previous edits")

    @validator('border_color')
    def validate_border_color(cls, v):
        """Validate hex color format (with or without #)."""
        if v is not None and not re.match(r'^#?[0-9A-Fa-f]{6}$', v):
            raise ValueError('Border color must be in hex format (e.g., #FF0000 or FF0000)')
        return v

class SpacingOptionsSchema(BaseModel):
    """Schema for spacing options"""
    paragraphs: bool = Field(False, description="Apply space to paragraphs")
    sentences: bool = Field(False, description="Apply space to sentences")
    from_original: bool = Field(False, description="Start from the original upload instead of chaining onto previous edits")


class KeywordOptionsSchema(BaseModel):
    """Schema for keyword extraction options"""
    max_keywords: Optional[int] = Field(5, ge=1, le=10, description="Maximum number of keywords per section")
    include_proper_nouns: Optional[bool] = Field(True, description="Include proper nouns (names, places)")
    model: Optional[str] = Field(None, description="Ollama model to use for keyword extraction (e.g., 'llama2', 'mistral')")
    from_original: bool = Field(False, description="Start from the original upload instead of chaining onto previous edits")


class HighlightingOptionsSchema(BaseModel):
    """Schema for part-of-speech text formatting options"""
    enabled: bool = Field(False, description="Enable text formatting")
    color: Optional[str] = Field("#000000", description="Text color in hex format")
    style: Optional[str] = Field(None, description="Text style: bold, italic, underline, or combinations like 'bold,italic'")
    font_size: Optional[int] = Field(None, ge=6, le=72, description="Font size in points (6-72)")
    font_family: Optional[str] = Field(None, description="Font family name (e.g., 'Times New Roman', 'Arial', 'Courier New')")
    nouns: Optional[bool] = Field(False, description="Format nouns")
    verbs: Optional[bool] = Field(False, description="Format verbs")
    adjectives: Optional[bool] = Field(False, description="Format adjectives")
    adverbs: Optional[bool] = Field(False, description="Format adverbs")
    from_original: bool = Field(False, description="Start from the original upload instead of chaining onto previous edits")

    @validator('color')
    def validate_color(cls, v):
        """Validate hex color format"""
        if v is not None:
            # Remove # if present
            color = v.lstrip('#')
            if not re.match(r'^[0-9A-Fa-f]{6}$', color):
                raise ValueError('Color must be in hex format (e.g., #FFFF00 or FFFF00)')
            return f"#{color}"  # Ensure it has # prefix
        return v

    @validator('style')
    def validate_style(cls, v):
        """Validate style value"""
        if v is not None:
            allowed = ['bold', 'italic', 'underline']
            styles = [s.strip().lower() for s in v.split(',')]
            for style in styles:
                if style not in allowed:
                    raise ValueError(f'Style must be one or more of: {", ".join(allowed)} (comma-separated)')
            return ','.join(styles)  # Normalize
        return v

    @validator('font_family')
    def validate_font_family(cls, v):
        """Validate font family"""
        if v is not None:
            # Common font families for validation
            common_fonts = [
                'times new roman', 'arial', 'courier new', 'calibri',
                'georgia', 'verdana', 'helvetica', 'open sans',
                'roboto', 'comic sans ms', 'impact'
            ]
            # Allow any font but warn if not common
            if v.lower() not in common_fonts:
                # Still allow it but could log a warning
                pass
        return v


class FormattingOptionsSchema(BaseModel):
    """Schema for formatting options"""
    font_name: Optional[str] = Field(None, description="Font family name")
    font_size: Optional[int] = Field(None, ge=6, le=72, description="Font size (6-72)")
    font_color: Optional[str] = Field(None, description="Font color in hex format")
    bold: Optional[bool] = Field(None, description="Apply bold formatting")
    italic: Optional[bool] = Field(None, description="Apply italic formatting")
    alignment: Optional[str] = Field(None, description="Text alignment")
    titles: Optional[bool] = Field(None, description="Apply document title formatting (Title style)")
    paragraphs: Optional[bool] = Field(None, description="Apply body text (paragraphs) formatting")
    section_titles: Optional[bool] = Field(None, description="Apply section title formatting (Heading 1 / Markdown #)")
    paragraphs_titles: Optional[bool] = Field(None, description="Apply paragraph title formatting (Heading 2+ / Markdown ##+)")
    captions: Optional[bool] = Field(None, description="Apply captions formatting")
    bibliography: Optional[bool] = Field(None, description="Apply bibliography formatting")
    from_original: bool = Field(False, description="Start from the original upload instead of chaining onto previous edits")
    theme: Optional[Dict[str, str]] = Field(
        None,
        description=(
            "Theme colors. Keys: 'positive'/'negative' seed hex colors and an "
            "optional 'scheme' (complementary, triadic, tetradic, even, analogous) "
            "used to derive additional colors when more than two roles are colored."
        ),
    )

    @validator('font_color')
    def validate_color(cls, v):
        """Validate hex color format"""
        if v is not None:
            # Remove # if present
            color = v.lstrip('#')
            if not re.match(r'^[0-9A-Fa-f]{6}$', color):
                raise ValueError('Color must be in hex format (e.g., #FF0000 or FF0000)')
        return v

    @validator('theme')
    def validate_theme(cls, v):
        """Validate theme seed colors and palette scheme."""
        if v is None:
            return v
        allowed_schemes = ('complementary', 'triadic', 'tetradic', 'even', 'analogous')
        for key in ('positive', 'negative'):
            color = v.get(key)
            if color is not None and not re.match(r'^#?[0-9A-Fa-f]{6}$', color):
                raise ValueError(
                    f"Theme '{key}' must be in hex format (e.g., #FF0000 or FF0000)"
                )
        scheme = v.get('scheme')
        if scheme is not None and scheme.lower() not in allowed_schemes:
            raise ValueError(
                f"Theme 'scheme' must be one of: {', '.join(allowed_schemes)}"
            )
        if scheme is not None:
            v['scheme'] = scheme.lower()
        return v

    @validator('alignment')
    def validate_alignment(cls, v):
        """Validate alignment value"""
        if v is not None:
            allowed = ['left', 'center', 'right', 'justify']
            if v.lower() not in allowed:
                raise ValueError(f'Alignment must be one of: {", ".join(allowed)}')
        return v.lower() if v else v


class SummarizeRequestSchema(BaseModel):
    """Schema for summarization request"""
    summary_type: Optional[str] = Field('brief', description="Type of summary")
    max_length: Optional[int] = Field(500, ge=50, le=2000, description="Maximum summary length")
    add_to_document: Optional[bool] = Field(
        False,
        description="Insert the summary at the top of the document, after the "
                    "title and before the body content"
    )
    model: Optional[str] = Field(
        None,
        description="Optional Ollama model tag to use for this request (e.g. "
                    "an FE 'AI model tier' reference model such as "
                    "'llama3.2:1b'). Falls back to the server's configured "
                    "default model when omitted."
    )

    @validator('summary_type')
    def validate_summary_type(cls, v):
        """Validate summary type"""
        allowed = ['brief', 'detailed', 'executive']
        if v.lower() not in allowed:
            raise ValueError(f'Summary type must be one of: {", ".join(allowed)}')
        return v.lower()


class ParaphraseRequestSchema(BaseModel):
    """Schema for paraphrase request"""
    style: Optional[str] = Field('simple', description="Paraphrasing style")
    sections: Optional[List[int]] = Field(None, description="Specific sections to paraphrase")
    apply_to_document: Optional[bool] = Field(
        False,
        description="Apply the paraphrase to the document body (rewriting the "
                    "content in place) and produce a new processed version"
    )
    model: Optional[str] = Field(
        None,
        description="Optional Ollama model tag to use for this request (e.g. "
                    "an FE 'AI model tier' reference model such as "
                    "'llama3.2:1b'). Falls back to the server's configured "
                    "default model when omitted."
    )

    @validator('style')
    def validate_style(cls, v):
        """Validate paraphrasing style"""
        allowed = ['casual', 'professional', 'simple']
        if v.lower() not in allowed:
            raise ValueError(f'Style must be one of: {", ".join(allowed)}')
        return v.lower()


class TextSummarizeRequestSchema(BaseModel):
    """Schema for direct text summarization"""
    text: str = Field(..., min_length=10, description="Text to summarize")
    max_length: Optional[int] = Field(500, ge=50, le=2000, description="Maximum summary length")
    model: Optional[str] = Field(None, description="Optional Ollama model tag to use for this request")


class TextParaphraseRequestSchema(BaseModel):
    """Schema for direct text paraphrasing"""
    text: str = Field(..., min_length=10, description="Text to paraphrase")
    style: Optional[str] = Field('simple', description="Paraphrasing style")
    model: Optional[str] = Field(None, description="Optional Ollama model tag to use for this request")

    @validator('style')
    def validate_style(cls, v):
        """Validate paraphrasing style"""
        allowed = ['casual', 'professional', 'simple']
        if v.lower() not in allowed:
            raise ValueError(f'Style must be one of: {", ".join(allowed)}')
        return v.lower()


def validate_schema(schema_class: BaseModel, data: Dict[str, Any]) -> BaseModel:
    """
    Validate data against a pydantic schema.

    Args:
        schema_class: Pydantic model class
        data: Data to validate

    Returns:
        Validated model instance

    Raises:
        ValidationException: If validation fails
    """
    try:
        return schema_class(**data)
    except Exception as e:
        raise ValidationException(
            f"Validation failed: {str(e)}",
            payload={'errors': str(e)}
        )


def validate_document_id(document_id: str) -> bool:
    """
    Validate document ID format (UUID).

    Args:
        document_id: Document ID to validate

    Returns:
        True if valid

    Raises:
        ValidationException: If invalid
    """
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(uuid_pattern, document_id, re.IGNORECASE):
        raise ValidationException(
            "Invalid document ID format",
            payload={'document_id': document_id}
        )
    return True
