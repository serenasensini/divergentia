# Bruno API Collection - Divergentia API

Collezione completa di test per l'API Divergentia Flask.

## 📋 Contenuto Collezione

Questa collezione Bruno include test per tutti i 12+ endpoint dell'API:

### 1️⃣ Utility Endpoints
- **01-Health-Check.bru** - Verifica stato API e connessione Ollama
- **02-Get-Supported-Formats.bru** - Lista formati supportati

### 2️⃣ Document Management
- **03-Upload-Document.bru** - Upload documento
- **04-Extract-Text.bru** - Estrazione testo da documento
- **05-Get-Document-Styles.bru** - Ottieni stili disponibili
- **06-Apply-Formatting.bru** - Applica framing (bordi) alle sezioni
- **06.1-Apply-Framing-Paragraphs.bru** - Applica bordi ai paragrafi
- **06.2-Apply-Framing-Multiple.bru** - Applica bordi multipli
- **06.3-Apply-Framing-Sentences.bru** - Applica bordi alle frasi
- **06.4-Apply-Framing-None.bru** - Test senza selezioni
- **11-Get-Document-Preview.bru** - Anteprima documento
- **12-Download-Document.bru** - Download documento

### 3️⃣ AI-Powered Features (Ollama)
- **07-Summarize-Document.bru** - Riassunto documento
- **08-Paraphrase-Document.bru** - Parafrasi documento
- **09-Summarize-Text-Direct.bru** - Riassunto testo diretto
- **10-Paraphrase-Text-Direct.bru** - Parafrasi testo diretto

## 🚀 Setup

### Prerequisiti
1. **Bruno** installato ([bruno.sh](https://www.usebruno.com/))
2. **API Flask** in esecuzione su `http://localhost:5000`
3. **Ollama** in esecuzione su `http://localhost:11434`

### Installazione Bruno
```bash
# Download da https://www.usebruno.com/downloads
# Oppure via package manager:

# Windows (winget)
winget install Bruno.Bruno

# macOS (brew)
brew install bruno

# Linux (snap)
snap install bruno
```

### Avviare API e Ollama
```powershell
# Terminal 1 - Avvia API
cd C:\Users\serena.sensini\WebstormProjects\divergentia\be
.\venv\Scripts\Activate.ps1
python run.py

# Terminal 2 - Avvia Ollama (se non già avviato)
ollama serve

# Terminal 3 - Pull modello se necessario
ollama pull llama2
```

## 📖 Uso della Collezione

### 1. Aprire la Collezione in Bruno
1. Apri Bruno
2. Click su "Open Collection"
3. Seleziona la cartella: `be/tests/integration/bruno`

### 2. Configurare le Variabili
La collezione usa queste variabili (già configurate in `bruno.json`):
- `base_url`: `http://localhost:5000/api`
- `document_id`: (auto-popolato dopo upload)

### 3. Eseguire i Test

#### Workflow Consigliato

**Test Rapido (senza Ollama):**
```
1. Health Check
2. Get Supported Formats
3. Upload Document
4. Extract Text
5. Get Document Styles
6. Get Document Preview
7. Download Document
```

**Test Completo (con Ollama):**
```
1. Health Check
2. Get Supported Formats
3. Upload Document
4. Extract Text
5. Summarize Document
6. Paraphrase Document
7. Apply Framing (Sections)
8. Apply Framing (Paragraphs)
9. Apply Framing (Multiple)
10. Download Document
```

**Test AI Direct (senza upload):**
```
1. Health Check
2. Summarize Text Direct
3. Paraphrase Text Direct
```

### 4. Eseguire Tutti i Test
Bruno permette di eseguire l'intera collezione:
1. Click destro sulla collezione
2. Seleziona "Run"
3. Tutti i test verranno eseguiti in sequenza

## 🔍 Dettagli Endpoint

### Health Check
```
GET /api/health
```
Verifica lo stato dell'API e della connessione a Ollama.

### Upload Document
```
POST /api/documents/upload
Content-Type: multipart/form-data
Body: file (binary)
```
⚠️ **Importante**: Dopo l'upload, il `document_id` viene automaticamente salvato come variabile per gli endpoint successivi.

### Summarize Document
```
POST /api/documents/{document_id}/summarize
Content-Type: application/json
Body: { "summary_type": "brief" }
```
Opzioni `summary_type`:
- `brief`: ~200 parole
- `detailed`: ~800 parole
- `executive`: ~400 parole

### Paraphrase Document
```
POST /api/documents/{document_id}/paraphrase
Content-Type: application/json
Body: { "style": "formal", "sections": [0, 1] }
```
Opzioni `style`:
- `formal`: Formale e professionale
- `casual`: Casual e conversazionale
- `professional`: Professionale business
- `simple`: Semplice e chiaro

### Apply Framing (Borders)
```
PUT /api/documents/{document_id}/format
Content-Type: application/json
Body: { 
  "framing": {
    "sections": true,
    "paragraphs": false,
    "subparagraphs": false,
    "sentences": false
  }
}
```

Applica bordi alle diverse parti del documento:

**Definizioni Parti:**
- **SENTENCE**: Da spazio + lettera maiuscola fino a punteggiatura
- **SUBPARAGRAPH**: Insieme di periodi complessi dipendenti tra loro
- **PARAGRAPH**: Insieme di sotto-paragrafi
- **SECTION**: Gruppo di paragrafi da [spazio + lettera maiuscola] a [punto + line break]

**Specifiche Bordi:**
- Larghezza: 1/2 pt (4 eighths)
- Colore: Nero (#000000)
- Stile: Solid

**Note:**
- Output file ha prefisso `edited_` (es. `edited_document.docx`)
- I bordi si applicano indipendentemente se multiple opzioni selezionate
- DOCX ha supporto completo, PDF implementazione base

## 📝 File di Test

La cartella include un file di esempio:
- **sample-document.txt** - Documento di test con contenuto sufficiente per testare tutte le funzionalità

## 🎯 Assertions

Ogni richiesta include assertions per validare:
- Status code corretto
- Presenza campi obbligatori nella response
- Valori attesi per campi specifici

Esempio:
```javascript
assert {
  res.status: eq 200
  res.body.status: eq healthy
  res.body.api_version: isDefined
}
```

## 🔐 Rate Limiting

Gli endpoint AI hanno rate limiting:
- Endpoint standard: 20 richieste/minuto
- Endpoint AI: 10 richieste/minuto

Se ricevi errore 429, attendi prima di riprovare.

## 🐛 Troubleshooting

### Errore: Connection refused
```
Soluzione: Verifica che l'API sia avviata su localhost:5000
```

### Errore: Ollama connection failed
```
Soluzione: 
1. Verifica Ollama sia avviato: curl http://localhost:11434/api/tags
2. Verifica modello scaricato: ollama pull llama2
```

### Errore: File upload failed
```
Possibili cause:
1. File troppo grande (>10MB)
2. Formato file non supportato
3. File non trovato (usa percorso assoluto o relativo corretto)
```

### Errore: Document not found (404)
```
Soluzione: Esegui prima l'upload del documento per ottenere un document_id valido
```

## 📊 Variabili Bruno

### Variabili di Collezione
Definite in `bruno.json`:
```json
vars {
  base_url: http://localhost:5000/api
  document_id: 
}
```

### Variabili di Runtime
Il `document_id` viene popolato automaticamente dallo script post-response dell'endpoint Upload:
```javascript
script:post-response {
  if (res.body.document_id) {
    bru.setVar("document_id", res.body.document_id);
  }
}
```

## 🎨 Personalizzazione

### Cambiare Base URL
Per testare su server diverso:
1. Apri `bruno.json`
2. Modifica `base_url`
```json
vars {
  base_url: https://api.production.com/api
}
```

### Aggiungere Autenticazione
Se l'API richiede autenticazione, aggiungi in ogni .bru:
```
auth: bearer
```

E configura il token nelle variabili di collezione.

## 📈 Best Practices

1. **Esegui Health Check** prima di ogni sessione di test
2. **Usa il file sample** fornito per test consistenti
3. **Salva i document_id** importanti per test futuri
4. **Rispetta i rate limits** per evitare 429 errors
5. **Controlla Ollama** prima di testare endpoint AI

## 🔄 Workflow Completo di Esempio

```
1. Health Check ✓
   → Verifica API e Ollama operativi

2. Get Supported Formats ✓
   → Conferma formati disponibili

3. Upload Document ✓
   → Carica sample-document.txt o bozza_progetto.docx
   → Salva document_id automaticamente

4. Extract Text ✓
   → Estrai contenuto testuale
   → Verifica text_content presente

5. Summarize Document ✓
   → Genera riassunto brief
   → Controlla key_points

6. Paraphrase Document ✓
   → Parafrasa in stile formal
   → Verifica paraphrased_sections

7. Apply Framing - Sections ✓
   → Applica bordi alle sezioni
   → Controlla success: true e borders_applied

8. Apply Framing - Paragraphs ✓
   → Applica bordi ai paragrafi
   → Verifica output_path con prefisso "edited_"

9. Apply Framing - Multiple ✓
   → Applica bordi a sezioni E paragrafi
   → Verifica bordi indipendenti

10. Download Document ✓
    → Scarica documento con bordi
    → Salva file localmente e verifica visualmente
```

## 📞 Support

Per problemi o domande:
1. Controlla i log dell'API: `be/app.log`
2. Verifica configurazione: `be/.env`
3. Consulta README: `be/README.md`

## 🎉 Happy Testing!

La collezione è pronta per testare tutte le funzionalità dell'API Divergentia!
