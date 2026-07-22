"""
File Upload and Handling Utilities
"""
import os
import logging
import magic
from typing import Tuple, Optional
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app

from app.exceptions.custom_exceptions import (
    FileUploadException,
    ValidationException
)

logger = logging.getLogger(__name__)

# Most Linux filesystems (ext4, xfs, ...) cap a single path component at 255
# bytes. We keep well under that so downstream code can still prepend prefixes
# (e.g. "spacing_<timestamp>_") and suffixes without hitting ENAMETOOLONG,
# which otherwise surfaces to the client as a 400 (upload) or 422 (processing).
MAX_FILENAME_LENGTH = 200


def cap_filename(filename: str, max_len: int = MAX_FILENAME_LENGTH) -> str:
    """Ensure a filename stays within filesystem length limits.

    The extension is always preserved; only the stem is truncated (from the
    end) when the whole name would exceed ``max_len``. This prevents unbounded
    growth when processed files are downloaded and re-uploaded/re-processed.

    Args:
        filename: The proposed filename (no directory component).
        max_len: Maximum allowed length for the resulting filename.

    Returns:
        A filename whose length is at most ``max_len``.
    """
    if len(filename) <= max_len:
        return filename

    path = Path(filename)
    ext = path.suffix
    stem = path.stem
    keep = max_len - len(ext)
    if keep < 1:
        # Pathological case: the extension alone is too long.
        return filename[:max_len]
    return stem[:keep] + ext


def validate_file(filename: str, file_size: int) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file.

    Args:
        filename: Original filename
        file_size: File size in bytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if filename is provided
    if not filename:
        return False, "No filename provided"

    # Check file extension
    file_extension = Path(filename).suffix.lower().lstrip('.')
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', set())

    if file_extension not in allowed_extensions:
        return False, f"File type '{file_extension}' not allowed. Allowed types: {', '.join(allowed_extensions)}"

    # Check file size
    max_size = current_app.config.get('MAX_UPLOAD_SIZE', 10485760)
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        return False, f"File size exceeds maximum allowed size of {max_size_mb:.1f}MB"

    return True, None


def save_uploaded_file(file, upload_folder: str) -> Tuple[str, str]:
    """
    Save uploaded file securely.

    Args:
        file: FileStorage object from Flask
        upload_folder: Folder to save file

    Returns:
        Tuple of (file_path, secure_filename)

    Raises:
        FileUploadException: If save fails
    """
    try:
        # Secure the filename
        original_filename = file.filename
        secured = secure_filename(original_filename)

        # Generate unique filename to avoid collisions
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        file_extension = Path(secured).suffix
        filename_without_ext = Path(secured).stem

        # Cap the human-readable stem so the final name (stem + "_" + 8-char id
        # + extension) stays within filesystem limits even when the uploaded
        # file already carries a long, previously-accumulated name.
        max_stem = MAX_FILENAME_LENGTH - len(file_extension) - (len(unique_id) + 1)
        if max_stem > 0 and len(filename_without_ext) > max_stem:
            filename_without_ext = filename_without_ext[:max_stem]

        unique_filename = f"{filename_without_ext}_{unique_id}{file_extension}"

        # Create upload folder if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)

        # Save file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        logger.info(f"File saved: {file_path}")

        return file_path, original_filename

    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}")
        raise FileUploadException(f"Failed to save file: {str(e)}")


def detect_mime_type(file_path: str) -> str:
    """
    Detect MIME type of file.

    Args:
        file_path: Path to file

    Returns:
        MIME type string
    """
    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(file_path)
        logger.debug(f"Detected MIME type: {mime_type} for {file_path}")
        return mime_type
    except Exception as e:
        logger.warning(f"Failed to detect MIME type: {str(e)}")
        # Fallback to extension-based detection
        extension = Path(file_path).suffix.lower()
        mime_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.rtf': 'application/rtf'
        }
        return mime_map.get(extension, 'application/octet-stream')


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.

    Args:
        file_path: Path to file

    Returns:
        File size in bytes
    """
    return os.path.getsize(file_path)


def delete_file(file_path: str) -> bool:
    """
    Delete file safely.

    Args:
        file_path: Path to file

    Returns:
        True if deleted, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to delete file {file_path}: {str(e)}")
        return False


def ensure_directory_exists(directory: str) -> None:
    """
    Ensure directory exists, create if it doesn't.

    Args:
        directory: Directory path
    """
    os.makedirs(directory, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    return secure_filename(filename)
