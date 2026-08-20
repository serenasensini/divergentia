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

# Number of bytes read from the start of an upload to sniff its real content
# type (magic bytes). Large enough to cover the ZIP local-file-header magic
# used by DOCX/XLSX/... and the OLE2 compound-file header used by legacy DOC,
# small enough to never meaningfully impact upload latency.
MAGIC_SNIFF_BYTES = 4096

# Canonical MIME types accepted for each supported extension, used to
# validate uploads *by content* (via libmagic) rather than trusting the
# filename extension alone. Several real-world variants are listed per type
# because different libmagic versions/OS builds report DOCX/DOC slightly
# differently (e.g. an empty/near-empty DOCX can be sniffed as plain 'zip'
# before python-docx even opens it).
ALLOWED_CONTENT_TYPES = {
    'pdf': {'application/pdf'},
    'docx': {
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/zip',  # DOCX is a ZIP container; some libmagic builds stop there.
    },
    'doc': {
        'application/msword',
        'application/x-ole-storage',
        'application/vnd.ms-office',
    },
    'txt': {'text/plain', 'text/x-python', 'inode/x-empty', 'application/octet-stream'},
}


def _looks_like_text(sample: bytes) -> bool:
    """Heuristic: True if ``sample`` contains no NUL bytes and decodes as UTF-8.

    Used as a permissive fallback for ``.txt`` uploads: libmagic's exact MIME
    label for short/ASCII samples is not always 'text/plain' (e.g. very short
    buffers), so a plain "no binary junk, valid UTF-8" check avoids false
    rejections of legitimate plain-text files.
    """
    if b"\x00" in sample:
        return False
    try:
        sample.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False



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


def validate_file_content(file, claimed_extension: str) -> Tuple[bool, Optional[str]]:
    """
    Validate an uploaded file's *actual* content type against what its
    filename extension claims, using magic-byte (libmagic) content sniffing.

    This defends against the classic "spoofed upload" attack where a
    malicious payload (e.g. an executable or script) is simply renamed with
    an allowed extension (e.g. ``.docx``) to slip past extension-only checks.

    The check is content-based and does not depend on the file being saved
    to disk yet: it reads a small buffer from the *start* of the stream and
    restores the original stream position afterwards, so the caller can
    still ``file.save(...)`` the full, untouched stream.

    Args:
        file: A file-like/FileStorage object (must support ``read``/``seek``).
        claimed_extension: The extension the upload claims to be (e.g. 'docx',
            without the leading dot).

    Returns:
        Tuple of (is_valid, error_message).
    """
    claimed_extension = claimed_extension.lower().lstrip('.')
    allowed_types = ALLOWED_CONTENT_TYPES.get(claimed_extension)
    if not allowed_types:
        # Unknown extension: let the caller's extension check handle it.
        return True, None

    try:
        file.seek(0)
        sample = file.read(MAGIC_SNIFF_BYTES)
        file.seek(0)
    except Exception as e:
        logger.warning(f"Could not read upload stream for content sniffing: {str(e)}")
        return True, None  # Fail open: don't block uploads on a sniffing glitch.

    if not sample:
        return False, "Uploaded file is empty"

    try:
        detected_type = magic.Magic(mime=True).from_buffer(sample)
    except Exception as e:
        logger.warning(f"Content sniffing failed ({str(e)}); skipping content validation")
        return True, None

    if detected_type in allowed_types:
        return True, None

    # Permissive fallback for .txt: libmagic's exact label for short/ASCII
    # samples isn't always 'text/plain', so accept any content that looks
    # like real text (no NUL bytes, valid UTF-8) instead of only comparing
    # to a fixed MIME string.
    if claimed_extension == 'txt' and _looks_like_text(sample):
        return True, None

    logger.warning(
        f"Content/extension mismatch: claimed '.{claimed_extension}' but "
        f"detected content type '{detected_type}'"
    )
    return False, (
        f"File content does not match its '.{claimed_extension}' extension "
        f"(detected: {detected_type}). The file may be corrupted or "
        f"mislabeled."
    )



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
        # Secure the filename: werkzeug's secure_filename() strips directory
        # separators, '..' segments and other unsafe characters.
        original_filename = file.filename
        secured = secure_filename(original_filename)

        # secure_filename() can legitimately return an empty string for
        # filenames made entirely of unsafe characters (e.g. "../../etc/passwd",
        # "????.docx", or a name using only non-ASCII characters it strips).
        # Saving with an empty stem would produce a hidden/malformed filename;
        # reject explicitly with a clear error instead.
        if not secured or not Path(secured).stem:
            raise FileUploadException(
                "The uploaded filename is invalid or unsafe; please rename the file "
                "using standard letters, numbers, dashes or underscores."
            )

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

        # Defense in depth: even though secure_filename() already strips path
        # separators and '..' segments, explicitly confirm the resolved path
        # still lives inside upload_folder before writing to disk. This
        # guards against directory traversal regressions in this or future
        # code paths that build file_path differently.
        real_upload_folder = os.path.realpath(upload_folder)
        real_file_path = os.path.realpath(file_path)
        if os.path.commonpath([real_upload_folder, real_file_path]) != real_upload_folder:
            logger.error(
                f"Rejected upload: resolved path '{real_file_path}' escapes "
                f"upload folder '{real_upload_folder}'"
            )
            raise FileUploadException("Invalid upload path")

        file.save(file_path)

        logger.info(f"File saved: {file_path}")

        return file_path, original_filename

    except FileUploadException:
        raise
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
            '.txt': 'text/plain'
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
