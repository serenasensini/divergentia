# Divergentia API - Bruno Collection Index

## 📚 Collection Overview

**Total Requests:** 21
**API Version:** 1.0.0
**Base URL:** http://localhost:5000/api

---

## 🗂️ Request Categories

### 1. Health & Information (2 requests)
| # | Name | Method | Endpoint | Description |
|---|------|--------|----------|-------------|
| 01 | Health Check | GET | `/health` | API status check |
| 02 | Get Supported Formats | GET | `/formats/supported` | List supported file formats |

### 2. Document Management (10 requests)
| # | Name | Method | Endpoint | Description |
|---|------|--------|----------|-------------|
| 03 | Upload Document | POST | `/documents/upload` | Upload file |
| 04 | Extract Text | POST | `/documents/{id}/extract-text` | Extract text content |
| 05 | Get Document Styles | GET | `/documents/{id}/styles` | Available formatting options |
| 06 | Apply Framing - Sections | PUT | `/documents/{id}/format` | Apply borders to sections |
| 06.1 | Apply Framing - Paragraphs | PUT | `/documents/{id}/format` | Apply borders to paragraphs |
| 06.2 | Apply Framing - Multiple | PUT | `/documents/{id}/format` | Apply borders to multiple parts |
| 06.3 | Apply Framing - Sentences | PUT | `/documents/{id}/format` | Apply borders to sentences |
| 06.4 | Apply Framing - None | PUT | `/documents/{id}/format` | Test with no borders |
| 11 | Get Document Preview | GET | `/documents/{id}/preview` | Document preview |
| 12 | Download Document | GET | `/documents/{id}/download` | Download file |

### 3. AI-Powered Operations (6 requests)
| # | Name | Method | Endpoint | Description |
|---|------|--------|----------|-------------|
| 07 | Summarize Document | POST | `/documents/{id}/summarize` | Generate summary |
| 07.1 | Summarize Document - Detailed | POST | `/documents/{id}/summarize` | Detailed summary variant |
| 08 | Paraphrase Document | POST | `/documents/{id}/paraphrase` | Paraphrase content |
| 08.1 | Paraphrase Document - Casual | POST | `/documents/{id}/paraphrase` | Casual style variant |
| 09 | Summarize Text Direct | POST | `/text/summarize` | Summarize without upload |
| 10 | Paraphrase Text Direct | POST | `/text/paraphrase` | Paraphrase without upload |

### 4. Error Test Cases (3 requests)
| # | Name | Method | Endpoint | Expected Status |
|---|------|--------|----------|-----------------|
| 99.1 | Invalid File Type | POST | `/documents/upload` | 400 |
| 99.2 | Invalid Document ID | GET | `/documents/{invalid}/preview` | 400 |
| 99.3 | Document Not Found | GET | `/documents/{uuid}/preview` | 404 |

---

## 🔄 Testing Workflows

### Quick Test (No AI)
```
01 → 02 → 03 → 04 → 05 → 11 → 12
```
⏱️ Duration: ~5 seconds

### Full AI Test
```
01 → 02 → 03 → 04 → 07 → 08 → 06 → 12
```
⏱️ Duration: ~30-60 seconds (depends on Ollama)

### Direct AI Test
```
01 → 09 → 10
```
⏱️ Duration: ~15-30 seconds

### Error Testing
```
99.1 → 99.2 → 99.3
```
⏱️ Duration: ~2 seconds

---

## 📊 Response Status Codes

| Code | Description | Endpoints |
|------|-------------|-----------|
| 200 | Success | All GET, POST (non-creation) |
| 201 | Created | Upload Document |
| 400 | Bad Request | Invalid input, file type |
| 404 | Not Found | Invalid document_id |
| 429 | Rate Limited | Too many AI requests |
| 500 | Server Error | Internal errors |
| 503 | Service Unavailable | Ollama connection failed |

---

## 🔧 Environment Variables

### Local Environment
```
base_url: http://localhost:5000/api
document_id: (auto-populated)
```

### Production Environment
```
base_url: https://api.production.com/api
document_id: (auto-populated)
```

---

## 📝 Request Body Schemas

### Upload Document
```
Content-Type: multipart/form-data
Body: file (binary)
```

### Apply Framing (Borders)
```json
{
  "framing": {
    "sections": false,      // Apply borders to sections
    "paragraphs": false,    // Apply borders to paragraphs
    "subparagraphs": false, // Apply borders to subparagraphs
    "sentences": false      // Apply borders to sentences
  }
}
```

**Output:** File with prefix `edited_` (e.g., `edited_document.docx`)

**Border Specifications:**
- Width: 1/2 pt (4 eighths)
- Color: Black (#000000)
- Style: Solid

### Summarize Document
```json
{
  "summary_type": "brief"  // brief | detailed | executive
}
```

### Paraphrase Document
```json
{
  "style": "formal",       // formal | casual | professional | simple
  "sections": [0, 1, 2]    // optional
}
```

### Summarize Text Direct
```json
{
  "text": "Your text here...",
  "max_length": 500
}
```

### Paraphrase Text Direct
```json
{
  "text": "Your text here...",
  "style": "formal"
}
```

---

## ⚡ Rate Limits

| Category | Limit | Affected Endpoints |
|----------|-------|-------------------|
| Standard | 20/min | Upload, Formatting, Download |
| AI Operations | 10/min | Summarize, Paraphrase |

---

## 📦 Files Included

```
bruno/
├── bruno.json                              # Collection config
├── README.md                               # Full documentation
├── COLLECTION_INDEX.md                     # This file
├── sample-document.txt                     # Test file
├── bozza_progetto_divergent_IA_versione_B_estesa.docx  # Test DOCX
├── environments/
│   ├── local.bru                          # Local env vars
│   └── production.bru                     # Prod env vars
├── 01-Health-Check.bru
├── 02-Get-Supported-Formats.bru
├── 03-Upload-Document.bru
├── 04-Extract-Text.bru
├── 05-Get-Document-Styles.bru
├── 06-Apply-Formatting.bru                 # Framing - Sections
├── 06.1-Apply-Framing-Paragraphs.bru      # Framing - Paragraphs
├── 06.2-Apply-Framing-Multiple.bru        # Framing - Multiple
├── 06.3-Apply-Framing-Sentences.bru       # Framing - Sentences
├── 06.4-Apply-Framing-None.bru            # Framing - None
├── 07-Summarize-Document.bru
├── 07.1-Summarize-Document-Detailed.bru
├── 08-Paraphrase-Document.bru
├── 08.1-Paraphrase-Document-Casual.bru
├── 09-Summarize-Text-Direct.bru
├── 10-Paraphrase-Text-Direct.bru
├── 11-Get-Document-Preview.bru
├── 12-Download-Document.bru
├── 99.1-Error-Invalid-File-Type.bru
├── 99.2-Error-Invalid-Document-ID.bru
└── 99.3-Error-Document-Not-Found.bru
```

---

## 🎯 Quick Start

1. **Open in Bruno**: Open the `bruno` folder as a collection
2. **Select Environment**: Choose "local" environment
3. **Start API**: Ensure Flask API is running
4. **Start Ollama**: For AI features, ensure Ollama is running
5. **Run Tests**: Execute requests in sequence or use "Run Collection"

---

## 🔍 Testing Tips

- ✅ Always start with Health Check
- ✅ Upload document before testing document-specific endpoints
- ✅ Check rate limits when testing AI endpoints
- ✅ Use provided sample-document.txt for consistency
- ✅ document_id is auto-saved after upload
- ✅ Test error cases separately

---

## 📞 Need Help?

- Full docs: `README.md` in this folder
- API docs: `be/README.md`
- Angular integration: `be/ANGULAR_INTEGRATION.md`

---

**Last Updated:** 2026-02-06
**Collection Version:** 1.0.0
