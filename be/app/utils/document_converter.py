"""
Document Conversion Utilities.

The core editing features (framing, spacing, highlighting, keywords, formatting)
operate on Word documents through ``python-docx`` and therefore require a real,
paragraph-based DOCX file. Legacy ``.doc`` and ``.pdf`` uploads are transparently
converted to DOCX at upload time so every downstream operation sees a uniform
DOCX working file:

* ``.doc`` -> DOCX via a headless LibreOffice process (``soffice --headless``).
  This preserves the document structure with high fidelity. The binary is
  provided by the backend image (see ``be/Dockerfile``).
* ``.pdf`` -> DOCX by extracting the text with PyMuPDF and rebuilding real
  paragraphs. A LibreOffice PDF import would instead place text in Draw-style
  text frames that ``python-docx`` cannot read as paragraphs, leaving the
  editing pipeline with nothing to work on; the text-reflow approach yields a
  fully editable document (graphic layout is intentionally not preserved).

When a required engine is unavailable the conversion raises a
``FileProcessingException`` with a clear, actionable message.
"""
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
from docx import Document
from flask import current_app

from app.exceptions.custom_exceptions import FileProcessingException

logger = logging.getLogger(__name__)

# Uploaded formats that are not directly editable and must be converted to DOCX
# before any processing. TXT and DOCX are handled natively and never converted.
CONVERTIBLE_EXTENSIONS = {'doc', 'pdf'}


def needs_conversion(extension: str) -> bool:
    """Return True when a file of the given extension must be converted to DOCX.

    Args:
        extension: File extension without a leading dot (case-insensitive).

    Returns:
        True if the extension is one we convert to DOCX before processing.
    """
    return extension.lower().lstrip('.') in CONVERTIBLE_EXTENSIONS


def convert_to_docx(src_path: str, out_dir: Optional[str] = None) -> str:
    """Convert a ``.doc`` or ``.pdf`` file to an editable DOCX.

    Dispatches to the appropriate engine based on the source extension.

    Args:
        src_path: Path to the source ``.doc`` / ``.pdf`` file.
        out_dir: Directory to write the converted DOCX into. Defaults to the
            source file's own directory.

    Returns:
        Absolute path to the produced ``.docx`` file.

    Raises:
        FileProcessingException: If the format is unsupported, the engine is
            missing/fails, or no output is produced.
    """
    src = Path(src_path)
    if not src.exists():
        raise FileProcessingException(f"Source file not found for conversion: {src_path}")

    extension = src.suffix.lower().lstrip('.')
    if extension not in CONVERTIBLE_EXTENSIONS:
        raise FileProcessingException(
            f"Cannot convert '{extension}' to DOCX; only {sorted(CONVERTIBLE_EXTENSIONS)} are supported."
        )

    out_directory = Path(out_dir) if out_dir else src.parent
    out_directory.mkdir(parents=True, exist_ok=True)
    produced = out_directory / f"{src.stem}.docx"

    if extension == 'pdf':
        return _convert_pdf_via_pymupdf(src, produced)
    return _convert_doc_via_libreoffice(src, out_directory, produced)


def _convert_pdf_via_pymupdf(src: Path, produced: Path) -> str:
    """Build an editable DOCX from a PDF's extracted text using PyMuPDF.

    Text blocks are emitted in reading order as individual paragraphs. Graphic
    layout is not preserved; the goal is a paragraph-based document the editing
    features can operate on.

    Args:
        src: Path to the source PDF.
        produced: Target path of the DOCX to write.

    Returns:
        Absolute path to the produced ``.docx`` file.

    Raises:
        FileProcessingException: If the PDF cannot be opened or contains no
            extractable text (e.g. a scanned/image-only PDF).
    """
    logger.info("Converting %s to DOCX via PyMuPDF text extraction", src.name)
    try:
        pdf = fitz.open(str(src))
    except Exception as exc:  # noqa: BLE001 - surface a clean message
        raise FileProcessingException(
            f"Failed to open PDF '{src.name}'. Please ensure it is a valid PDF document."
        ) from exc

    document = Document()
    paragraphs_added = 0
    try:
        for page in pdf:
            # ``blocks`` returns (x0, y0, x1, y1, text, block_no, block_type);
            # sort=True yields natural top-to-bottom, left-to-right reading order.
            for block in page.get_text("blocks", sort=True):
                text = (block[4] or "").strip()
                if not text:
                    continue
                # Reflow soft-wrapped lines within a block into a single
                # paragraph so downstream sentence/paragraph logic behaves.
                paragraph_text = " ".join(line.strip() for line in text.splitlines() if line.strip())
                if paragraph_text:
                    document.add_paragraph(paragraph_text)
                    paragraphs_added += 1
    finally:
        pdf.close()

    if paragraphs_added == 0:
        raise FileProcessingException(
            f"No extractable text found in PDF '{src.name}'. Scanned/image-only "
            f"PDFs are not supported (OCR is not available)."
        )

    document.save(str(produced))
    logger.info("Converted %s -> %s (%d paragraphs)", src.name, produced.name, paragraphs_added)
    return str(produced)


def _libreoffice_bin() -> str:
    """Resolve the LibreOffice executable name/path from config or defaults."""
    try:
        configured = current_app.config.get('LIBREOFFICE_BIN')
    except RuntimeError:
        # No application context (e.g. unit tests calling the helper directly).
        configured = None
    return configured or os.getenv('LIBREOFFICE_BIN', 'soffice')


def _conversion_timeout() -> int:
    """Resolve the conversion timeout (seconds) from config or defaults."""
    try:
        return int(current_app.config.get('DOC_CONVERSION_TIMEOUT', 120))
    except RuntimeError:
        return int(os.getenv('DOC_CONVERSION_TIMEOUT', 120))


def _convert_doc_via_libreoffice(src: Path, out_directory: Path, produced: Path) -> str:
    """Convert a legacy ``.doc`` to DOCX via a headless LibreOffice process.

    Args:
        src: Path to the source ``.doc``.
        out_directory: Directory LibreOffice writes the output into.
        produced: Expected path of the produced ``.docx``.

    Returns:
        Absolute path to the produced ``.docx`` file.

    Raises:
        FileProcessingException: If LibreOffice is missing, times out, or the
            expected output file is not produced.
    """
    soffice = _libreoffice_bin()
    if not os.path.isabs(soffice) and shutil.which(soffice) is None:
        raise FileProcessingException(
            "LibreOffice ('soffice') is not installed or not on PATH; cannot "
            "convert DOC uploads to DOCX. Install LibreOffice or set LIBREOFFICE_BIN."
        )

    # An isolated, throwaway user profile avoids the shared-profile lock that
    # otherwise makes concurrent/headless conversions fail, and works even when
    # HOME is not writable.
    with tempfile.TemporaryDirectory(prefix='lo_profile_') as profile_dir:
        cmd = [
            soffice,
            '--headless',
            '--norestore',
            '--nolockcheck',
            f'-env:UserInstallation=file://{profile_dir}',
            '--convert-to', 'docx:MS Word 2007 XML',
            '--outdir', str(out_directory),
            str(src),
        ]

        logger.info("Converting %s to DOCX via LibreOffice", src.name)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=_conversion_timeout(),
                check=False,
            )
        except FileNotFoundError as exc:
            raise FileProcessingException(
                "LibreOffice ('soffice') is not installed or not on PATH; cannot "
                "convert DOC uploads to DOCX."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise FileProcessingException(
                f"Conversion of '{src.name}' to DOCX timed out."
            ) from exc

    if result.returncode != 0 or not produced.exists():
        logger.error(
            "LibreOffice conversion failed (rc=%s): %s%s",
            result.returncode, result.stdout, result.stderr,
        )
        raise FileProcessingException(
            f"Failed to convert '{src.name}' to DOCX. Please ensure the file is a "
            f"valid DOC document."
        )

    logger.info("Converted %s -> %s", src.name, produced.name)
    return str(produced)

