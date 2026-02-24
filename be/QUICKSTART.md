# Quick Start Guide

## Setup Steps

### 1. Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configure Environment
```powershell
# .env file is already created, edit if needed
notepad .env
```

### 4. Install and Run Ollama
```powershell
# Download from https://ollama.ai
# After installation, pull a model:
ollama pull llama2
```

### 5. Run the Application
```powershell
python run.py
```

### 6. Test the API
```powershell
# Health check
curl http://localhost:5000/api/health

# Supported formats
curl http://localhost:5000/api/formats/supported
```

## API is now running at http://localhost:5000

For full documentation, see README.md
