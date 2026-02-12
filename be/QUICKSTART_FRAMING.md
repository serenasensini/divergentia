# Quick Start Guide - Framing Feature Testing

## 🚀 Avvio Rapido

### 1. Avviare l'API Flask

```powershell
cd C:\Users\serena.sensini\WebstormProjects\divergentia\be
.\venv\Scripts\Activate.ps1
python run.py
```

L'API sarà disponibile su: `http://localhost:5000`

---

## 🧪 Test con Bruno

### Prerequisiti
- API Flask in esecuzione
- Bruno installato
- File di test disponibile: `bozza_progetto_divergent_IA_versione_B_estesa.docx`

### Workflow di Test Completo

#### 1. Health Check
```
GET http://localhost:5000/api/health
```
✅ Verifica che API sia operativa

#### 2. Upload Document
```
POST http://localhost:5000/api/documents/upload
Content-Type: multipart/form-data

file: bozza_progetto_divergent_IA_versione_B_estesa.docx
```
✅ Salva il `document_id` dalla risposta

#### 3. Extract Text
```
POST http://localhost:5000/api/documents/{document_id}/extract-text
```
✅ Verifica che il testo venga estratto

#### 4. Apply Framing - Sections Only
```
PUT http://localhost:5000/api/documents/{document_id}/format
Content-Type: application/json

{
  "framing": {
    "sections": true,
    "paragraphs": false,
    "subparagraphs": false,
    "sentences": false
  }
}
```
✅ Output: `edited_bozza_progetto_divergent_IA_versione_B_estesa.docx`

#### 5. Download & Verify
```
GET http://localhost:5000/api/documents/{document_id}/download
```
✅ Apri il file e verifica i bordi sulle sezioni

#### 6. Upload di Nuovo (per test successivi)
```
POST http://localhost:5000/api/documents/upload
```
Ripeti upload per testare altre combinazioni

#### 7. Apply Framing - Paragraphs Only
```
PUT http://localhost:5000/api/documents/{new_document_id}/format

{
  "framing": {
    "sections": false,
    "paragraphs": true,
    "subparagraphs": false,
    "sentences": false
  }
}
```

#### 8. Apply Framing - Multiple Parts
```
PUT http://localhost:5000/api/documents/{new_document_id}/format

{
  "framing": {
    "sections": true,
    "paragraphs": true,
    "subparagraphs": false,
    "sentences": false
  }
}
```

---

## 🔍 Verifica Visiva

### Aprire il File Modificato

1. Naviga a: `C:\Users\serena.sensini\WebstormProjects\divergentia\be\outputs\`
2. Apri `edited_bozza_progetto_divergent_IA_versione_B_estesa.docx` con Microsoft Word

### Cosa Verificare

#### Sezioni (sections: true)
- [ ] Le sezioni che iniziano con " A. ", " B. ", etc. hanno bordi
- [ ] I bordi sono neri, solid, 1/2 pt
- [ ] I bordi circondano l'intera sezione

#### Paragrafi (paragraphs: true)
- [ ] Ogni paragrafo non vuoto ha un bordo
- [ ] I bordi sono applicati indipendentemente

#### Multiple Selections
- [ ] Se selezionate sezioni + paragrafi, entrambi hanno bordi
- [ ] I bordi possono sovrapporsi visivamente

---

## 🐛 Troubleshooting

### Errore: "framing field is required"
**Soluzione:** Assicurati che il body JSON includa il campo `"framing"`

```json
{
  "framing": {
    "sections": true,
    ...
  }
}
```

### Errore: "Document not found"
**Soluzione:** Usa un `document_id` valido ottenuto dall'upload

### Nessun Bordo Visibile
**Possibili Cause:**
1. Tutte le opzioni sono `false` → `borders_applied: 0`
2. Il documento non contiene le parti selezionate
3. Il formato del documento non è supportato

**Verifica:**
```json
{
  "success": true,
  "borders_applied": 0  // Se 0, nessun bordo applicato
}
```

### File Output Non Trovato
**Soluzione:** Verifica che la cartella `outputs/` esista:
```powershell
New-Item -ItemType Directory -Path "C:\Users\serena.sensini\WebstormProjects\divergentia\be\outputs" -Force
```

---

## 📊 Test Cases da Verificare

### Test Case 1: Solo Sezioni
```json
{
  "framing": {
    "sections": true,
    "paragraphs": false,
    "subparagraphs": false,
    "sentences": false
  }
}
```
**Expected:** Bordi solo sulle sezioni (A., B., etc.)

### Test Case 2: Solo Paragrafi
```json
{
  "framing": {
    "sections": false,
    "paragraphs": true,
    "subparagraphs": false,
    "sentences": false
  }
}
```
**Expected:** Bordi su ogni paragrafo

### Test Case 3: Sezioni + Paragrafi
```json
{
  "framing": {
    "sections": true,
    "paragraphs": true,
    "subparagraphs": false,
    "sentences": false
  }
}
```
**Expected:** Bordi su sezioni E paragrafi (indipendenti)

### Test Case 4: Tutte le Frasi
```json
{
  "framing": {
    "sections": false,
    "paragraphs": false,
    "subparagraphs": false,
    "sentences": true
  }
}
```
**Expected:** Bordi sui paragrafi contenenti frasi

### Test Case 5: Nessuna Selezione
```json
{
  "framing": {
    "sections": false,
    "paragraphs": false,
    "subparagraphs": false,
    "sentences": false
  }
}
```
**Expected:** `borders_applied: 0`, file creato ma senza bordi

---

## 🎯 Test con curl (Alternative a Bruno)

### Upload
```powershell
curl -X POST http://localhost:5000/api/documents/upload `
  -F "file=@C:\Users\serena.sensini\WebstormProjects\divergentia\be\tests\integration\bruno\Divergentia\bozza_progetto_divergent_IA_versione_B_estesa.docx"
```

### Apply Framing
```powershell
# Salva il document_id dalla risposta precedente
$documentId = "your-document-id-here"

curl -X PUT "http://localhost:5000/api/documents/$documentId/format" `
  -H "Content-Type: application/json" `
  -d '{"framing":{"sections":true,"paragraphs":false,"subparagraphs":false,"sentences":false}}'
```

### Download
```powershell
curl -X GET "http://localhost:5000/api/documents/$documentId/download" `
  --output edited_document.docx
```

---

## 📝 Log Debugging

### Controllare i Log
```powershell
Get-Content C:\Users\serena.sensini\WebstormProjects\divergentia\be\app.log -Tail 50
```

### Log Importanti da Cercare
```
INFO - Framing requested for document {id}
INFO - Applying framing to DOCX document
INFO - Identified X sections
INFO - Identified Y paragraphs
INFO - Applied borders to X sections
INFO - DOCX framing completed: N borders applied
```

---

## ✅ Success Indicators

### Response Success
```json
{
  "success": true,
  "output_path": "outputs/edited_document.docx",
  "format": "docx",
  "borders_applied": 5,  // > 0
  "framing_options": {
    "sections": true,
    "paragraphs": false,
    "subparagraphs": false,
    "sentences": false
  }
}
```

### Visual Verification
1. ✅ File `edited_*.docx` esiste in `outputs/`
2. ✅ File si apre correttamente in Word
3. ✅ Bordi visibili sulle parti selezionate
4. ✅ Bordi sono neri, solid, sottili (1/2 pt)

---

## 🎉 Test Completati!

Una volta verificati tutti i test cases:
- [ ] Sezioni con bordi
- [ ] Paragrafi con bordi
- [ ] Multiple selezioni
- [ ] Frasi con bordi
- [ ] Nessuna selezione (borders_applied: 0)

Il sistema di framing è completamente funzionante! 🚀

---

**Next Steps:**
1. Test con documenti di diverse dimensioni
2. Test con PDF (implementazione base)
3. Test performance con documenti molto grandi
4. Integrazione con Ollama per identificazione avanzata parti


