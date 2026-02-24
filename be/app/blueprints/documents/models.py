"""
Models for Document Management (Optional - for future database integration)
"""
from typing import Optional
from datetime import datetime


class Document:
    """Document model for database storage"""

    def __init__(
        self,
        id: str,
        original_filename: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        file_extension: str,
        created_at: Optional[datetime] = None,
        modified_at: Optional[datetime] = None,
        text_content: Optional[str] = None,
        formatted_path: Optional[str] = None
    ):
        self.id = id
        self.original_filename = original_filename
        self.file_path = file_path
        self.file_size = file_size
        self.mime_type = mime_type
        self.file_extension = file_extension
        self.created_at = created_at or datetime.utcnow()
        self.modified_at = modified_at
        self.text_content = text_content
        self.formatted_path = formatted_path

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'file_extension': self.file_extension,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
            'text_content': self.text_content,
            'formatted_path': self.formatted_path
        }
