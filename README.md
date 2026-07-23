# Divergentia

> A calm, gamified document workshop designed for neurodivergent minds.

Divergentia turns a plain `.docx`/`.pdf` into a more readable, accessibility-oriented
document through a friendly, game-like workshop. Upload a file, then apply
transformations — visual **framing** of sections/paragraphs/sentences, colour
**formatting**, **spacing**, part-of-speech **highlighting**, section **keyword**
extraction, and AI-powered **summarization/paraphrasing** — one step at a time,
with a live preview and download at every stage.

The interface is intentionally low-stimulation and configurable (theme, font —
including a dyslexia-friendly face —, text size and reduced motion) to support
neurodivergent users.

---

## Authors

Idea and design by **Serena Sensini** and **Martina Ricci**.

## License

This project is licensed under the
**Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**
license. You are free to use, share and adapt the work for **private and academic**
purposes, provided you give appropriate credit to the authors. **Commercial use is
not permitted.** See the [LICENSE](./LICENSE) file for the full terms.

---

## Architecture

| Layer | Stack | Location |
|-------|-------|----------|
| Front-end | React 18 + TypeScript + Vite | [`fe/`](./fe) |
| Back-end (API) | Flask + python-docx + PyMuPDF + spaCy (`it_core_news_lg`) | [`be/`](./be) |
| AI engine | [Ollama](https://ollama.ai) (local LLM, e.g. `llama3.2:3b`) | container / local |
| Orchestration | Docker / Podman Compose | [`docker-compose.yml`](./docker-compose.yml) |

The front-end (dev server on port **4200**) proxies `/api` to the Flask back-end
(port **5000**), which in turn talks to Ollama for the AI operations. The service
is **ephemeral by design**: the document registry lives in memory and is discarded
when the process stops — it is meant for single-shot local usage
(upload → edit → preview → download).

> `old/` contains a legacy Angular prototype and is **not** part of the current app.

---

## Prerequisites

- **Node.js** ≥ 18 and npm
- **Python** 3.12 (3.9+ works for the API)
- **Ollama** (for AI summarize/paraphrase) — optional if you don't use those features
- **Docker** or **Podman** (optional, for the containerised setup)

---

## Run locally (manual)

### 1. Back-end (Flask API)

```bash
cd be

# Create & activate a virtual environment
python3.12 -m venv venv
source venv/bin/activate          # Linux/macOS
# .\venv\Scripts\Activate.ps1     # Windows PowerShell

# Install runtime deps (and dev deps for tests/linting)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# The API uses the Italian spaCy model for NLP features.
# If it is not already installed, download it:
python -m spacy download it_core_news_lg

# Configure the environment (see variables below)
cp .env.example .env              # then edit as needed

# Start the API (http://localhost:5000)
python run.py
```

Common environment variables (all optional, sensible defaults shown):

```env
FLASK_ENV=development
SECRET_KEY=change-me
HOST=0.0.0.0
PORT=5000
CORS_ORIGINS=http://localhost:4200
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
MAX_UPLOAD_SIZE=10485760          # 10 MB
```

For AI features, make sure Ollama is running and the model is pulled:

```bash
ollama pull llama3.2:3b
curl http://localhost:11434/api/tags   # verify Ollama is up
```

### 2. Front-end (React + Vite)

```bash
cd fe
npm install
npm run dev                       # http://localhost:4200
```

The dev server proxies `/api` to `http://localhost:5000` by default. To point it
elsewhere, set `VITE_API_TARGET` before starting Vite.

---

## Run with Docker / Podman

`docker-compose.yml` bundles everything — the API, the web front-end (Vite build
served by Nginx), **and** a self-contained Ollama instance — so no external Ollama
installation is required. On first start the model is pulled into a named volume.

```bash
# From the repository root
docker compose up --build         # or: podman compose up --build
```

Once up:

- Web UI → <http://localhost:8080>
- API → <http://localhost:5000>

---

## Testing

**Back-end** (from `be/`):

```bash
pytest                            # run all tests
pytest --cov=app tests/           # with coverage
pytest -v                         # verbose
```

**Front-end** (from `fe/`):

```bash
npm test                          # unit tests (Vitest)
npm run test:integration          # integration tests
```

There is also a [Bruno](https://www.usebruno.com/) API collection under
[`be/tests/integration/bruno/`](./be/tests/integration/bruno).

---

## Project layout

```
divergentia/
├── be/                  # Flask API (document processing + AI)
├── fe/                  # React + Vite front-end (the workshop UI)
├── old/                 # Legacy Angular prototype (not used)
├── docker-compose.yml   # API + web + Ollama
├── LICENSE              # CC BY-NC 4.0
└── README.md
```

For the full API reference (endpoints, request/response examples, operation
chaining) see [`be/README.md`](./be/README.md).

