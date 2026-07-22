# Divergentia API - Flask Document Processing Service

RESTful API built with Flask for document processing with AI-powered summarization and paraphrasing using Ollama.

## Features

- 📄 **Document Upload**: Support for PDF, DOCX, TXT, RTF formats
- ✨ **Document Formatting**: Modify font, colors, size, alignment programmatically
- 🤖 **AI-Powered Text Processing**: 
  - Summarization (brief, detailed, executive)
  - Paraphrasing (formal, casual, professional, simple)
- 🔒 **Security**: Rate limiting, CORS, input validation, secure file handling
- 🏗️ **Architecture**: Clean separation with blueprints, services, repositories
- ✅ **Testing**: Unit and integration tests with pytest
- 🐳 **Docker Ready**: Container setup with docker-compose

## Prerequisites

- Python 3.9+
- Ollama running locally (http://localhost:11434)
- Git

## Quick Start

### 1. Clone and Setup

```powershell
cd path/to/divergentia/be

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# For Linux
source venv/bin/activate

# Install dependencies (runtime)
pip install -r requirements.txt

# For development/testing, also install the dev tools
pip install -r requirements-dev.txt
```

### 2. Configure Environment

```powershell
# Copy environment template
Copy-Item .env.example .env

# Edit .env and set your configuration
```

Required environment variables:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
CORS_ORIGINS=http://localhost:4200
```

### 3. Setup Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai)

```powershell
# Pull a model (e.g., llama2)
ollama pull llama2

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

### 4. Run the Application

```powershell
# Development mode
python run.py

# Production mode with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health & Info

| Endpoint | Method | Description | Notes |
|----------|--------|-------------|-------|
| `/api/health` | GET | Health check | Requires Ollama to be running |
| `/api/formats/supported` | GET | List supported formats | |

### Document Operations

| Endpoint | Method | Description | Notes |
|----------|--------|-------------|-------|
| `/api/documents/upload` | POST | Upload a document | Accepts PDF, DOCX, TXT, RTF |
| `/api/documents/{id}/extract-text` | POST | Extract the text content | |
| `/api/documents/{id}/format` | PUT | Apply formatting | Distinguishes four roles: `titles` = the main document Title style, `section_titles` = Heading 1 (Markdown `#`), `paragraphs_titles` = Heading 2 and deeper (Markdown `##`+), `paragraphs` = body text. Headings are classified by Word outline level, so custom/localised title styles are recognised too. The `theme` takes `positive`/`negative` seed colors plus an optional `scheme` (`complementary`, `triadic`, `tetradic`, `even`, `analogous`); when 3+ roles are colored, extra distinct colors are derived from the seeds so no role is left uncolored. |
| `/api/documents/{id}/framing` | PUT | Apply framing (borders) to document parts | Each part is framed in single-cell tables at the right granularity: `sections` = one table wrapping the whole section, `paragraphs` = one table per paragraph, `sentences` = one table per sentence. Every table is followed by an empty paragraph so adjacent tables don't merge into one grid. Parts use distinct default borders (section=double/2pt, paragraph=single/1pt, sentence=dashed/½pt), overridable via `border_style`/`border_width`/`border_color`. Precedence when combined: sections > paragraphs > sentences. |
| `/api/documents/{id}/spacing` | PUT | Add spacing between paragraphs/sentences | Adds a blank line around each paragraph (`paragraphs`) and a single line break between sentences (`sentences`). List items (ordered or unordered) are spaced with padding above and below each element instead of blank lines, so the list structure is preserved. |
| `/api/documents/{id}/keywords` | PUT | Extract and insert section keywords | Extracts keywords from each section and inserts them as a formatted paragraph above the section. The prefix is localised to the section language (e.g. "Parole chiave", "Keywords", "Mots-clés") and the keywords are separated from the section content by trailing spacing. |
| `/api/documents/{id}/highlighting` | PUT | Apply part-of-speech text highlighting | |
| `/api/documents/{id}/styles` | GET | List the styles available in the document | |
| `/api/documents/{id}/download` | GET | Download the processed document | Serves the latest processed version of the document (or the original if no processing has been applied). See [Chaining operations & downloading](#chaining-operations--downloading). |
| `/api/documents/{id}/preview` | GET | Get a document preview | |

### AI-Powered Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/documents/{id}/summarize` | POST | Summarize a document |
| `/api/documents/{id}/paraphrase` | POST | Paraphrase a document |
| `/api/text/summarize` | POST | Summarize text directly |
| `/api/text/paraphrase` | POST | Paraphrase text directly |

## Usage Examples

### Upload Document

```powershell
curl -X POST http://localhost:5000/api/documents/upload `
  -F "file=@document.pdf"
```

### Summarize Document

```powershell
curl -X POST http://localhost:5000/api/documents/{document-id}/summarize `
  -H "Content-Type: application/json" `
  -d '{"summary_type": "brief"}'
```

### Apply Formatting

```powershell
curl -X PUT http://localhost:5000/api/documents/{document-id}/format `
  -H "Content-Type: application/json" `
  -d '{
    "font_name": "Arial",
    "font_size": 12,
    "font_color": "#000000",
    "bold": false,
    "alignment": "left"
  }'
```

### Paraphrase Text

```powershell
curl -X POST http://localhost:5000/api/text/paraphrase `
  -H "Content-Type: application/json" `
  -d '{
    "text": "Your text here",
    "style": "formal"
  }'
```

## Chaining operations & downloading

Every processing endpoint (`format`, `framing`, `spacing`, `keywords`,
`highlighting`) works on a document identified by its `id` and returns a
reference to the result rather than a server file path:

```json
{
  "success": true,
  "document_id": "abc-123-def-456",
  "filename": "spacing_20260301120000_document.docx",
  "download_url": "/api/documents/abc-123-def-456/download"
}
```

Operations **chain by default**: each call reads the latest processed version of
the document and writes a new one. This means you can apply several operations in
sequence to the same document — for example add spacing and then framing — and
the changes accumulate:

1. `PUT /api/documents/{id}/spacing`  → produces version 1
2. `PUT /api/documents/{id}/framing`  → reads version 1, produces version 2
3. `GET /api/documents/{id}/download` → downloads version 2 (spacing **and** framing)

Always download using the `document_id` (via `download_url`); the download route
always serves the most recent processed version.

To ignore previous processing and start again from the originally uploaded file,
pass `"from_original": true` in the request body of any operation.

> The service is **ephemeral by design**: the document registry is kept in
> memory and is discarded when the process stops. It is meant for single-shot,
> local usage (upload → edit → preview → download), so nothing is persisted for
> future sessions. Run it with a single worker (the default in the provided
> Dockerfile) so the in-memory registry stays coherent for the one user.

## Project Structure

```
be/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration
│   ├── blueprints/              # API routes
│   │   └── documents/
│   │       ├── routes.py        # Document endpoints
│   │       ├── schemas.py       # Response schemas
│   │       └── models.py        # Data models
│   ├── services/                # Business logic
│   │   ├── ollama_service.py   # Ollama integration
│   │   ├── formatting_service.py
│   │   └── document_service.py
│   ├── repositories/            # Data access
│   ├── middleware/              # Error handling, security
│   ├── utils/                   # Utilities
│   └── exceptions/              # Custom exceptions
├── tests/                       # Test suite
├── uploads/                     # Upload directory
├── outputs/                     # Processed files
├── run.py                       # Application entry point
├── requirements.txt             # Dependencies
└── .env.example                 # Environment template
```

## Testing

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_ollama_service.py

# Run with verbose output
pytest -v
```

## Code Quality

```powershell
# Format code with black
black app/ tests/

# Lint with flake8
flake8 app/ tests/

# Type checking with mypy
mypy app/

# Run all quality checks
black app/ tests/ && flake8 app/ tests/ && mypy app/
```

## Running locally with Docker / Podman

The service is meant to be run locally for a single user. The image runs a
single worker with an in-memory, ephemeral document registry (nothing is
persisted between runs).

`docker-compose.yml` bundles everything you need — the API **and** a
self-contained Ollama instance — so no external Ollama installation is required.
On first start the model is pulled automatically into a named volume.

```bash
# Build and start API + Ollama (Docker)
docker compose up --build

# ...or with Podman
podman compose up --build
```

The bundled Ollama service is reachable by the API at `http://ollama:11434` over
the compose network; the model (`llama2` by default) is pulled on first run.
Change the model by editing `OLLAMA_MODEL` and the `ollama-pull` command in
`docker-compose.yml`.

To build/run just the API image against your own Ollama instead:

```bash
docker build -t divergentia-api .
docker run --rm -p 5000:5000 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  divergentia-api
```

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub.
