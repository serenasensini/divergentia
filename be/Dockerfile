# Lightweight image for the single-shot, local Divergentia API.
FROM docker.io/library/python:3.11-slim

# System deps:
#  - libmagic1: file-type detection
#  - libreoffice-writer: headless legacy DOC -> DOCX conversion
#    (PDF -> DOCX is handled in-process by PyMuPDF, so Draw is not needed)
#  - fonts-liberation: sane default fonts for the converted documents
#  - build tools for wheels that need compiling (removed afterwards).
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc g++ libmagic1 \
        libreoffice-writer fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install runtime Python dependencies (dev/test tools are intentionally excluded).
COPY requirements.txt .

ARG SPACY_MODEL=it_core_news_lg
ENV SPACY_MODEL=${SPACY_MODEL}

RUN pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download ${SPACY_MODEL}

# Drop the compilers once wheels are built to slim the final image.
RUN apt-get purge -y gcc g++ && apt-get autoremove -y

# Copy application code (see .dockerignore for what is excluded).
COPY . .

# Runtime directories for uploads and generated files.
RUN mkdir -p uploads outputs

# Run as a non-root user.
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

ENV FLASK_APP=run.py \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

EXPOSE 5000

# Single worker: the document registry is in-memory and shared per process for
# the one local user. Threads handle concurrent requests within that process.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", \
     "--workers", "1", "--threads", "4", "--timeout", "120", \
     "run:app"]
