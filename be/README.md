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
cd C:\Users\serena.sensini\WebstormProjects\divergentia\be

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# For Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
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

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/formats/supported` | GET | List supported formats |

### Document Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/documents/upload` | POST | Upload document |
| `/api/documents/{id}/extract-text` | POST | Extract text content |
| `/api/documents/{id}/format` | PUT | Apply formatting |
| `/api/documents/{id}/styles` | GET | Get available styles |
| `/api/documents/{id}/download` | GET | Download document |
| `/api/documents/{id}/preview` | GET | Get document preview |

### AI-Powered Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/documents/{id}/summarize` | POST | Summarize document |
| `/api/documents/{id}/paraphrase` | POST | Paraphrase document |
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

## Docker Deployment

```powershell
# Build image
docker build -t divergentia-api .

# Run with docker-compose
docker-compose up -d
```

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub.
