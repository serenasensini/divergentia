# Document Framing Feature

## 📖 Overview

The Document Framing feature allows users to apply borders to different structural parts of a document (sections, paragraphs, subparagraphs, sentences). This feature replaces the traditional font-based formatting with a visual framing system.

---

## 🎯 Use Cases

1. **Visual Document Structure:** Highlight different parts of a document for better readability
2. **Section Identification:** Clearly mark document sections
3. **Educational Materials:** Create worksheets with bordered sections
4. **Legal Documents:** Frame important clauses and paragraphs
5. **Document Review:** Visually separate parts for review/comments

---

## 🔧 API Endpoint

### `PUT /api/documents/{document_id}/format`

Apply borders to document parts.

#### Request Body

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

#### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `framing.sections` | boolean | Yes | Apply borders to sections |
| `framing.paragraphs` | boolean | Yes | Apply borders to paragraphs |
| `framing.subparagraphs` | boolean | Yes | Apply borders to subparagraphs |
| `framing.sentences` | boolean | Yes | Apply borders to sentences |

#### Response

```json
{
  "success": true,
  "output_path": "outputs/edited_document.docx",
  "format": "docx",
  "borders_applied": 5,
  "framing_options": {
    "sections": true,
    "paragraphs": false,
    "subparagraphs": false,
    "sentences": false
  }
}
```

---

## 📐 Document Part Definitions

### SENTENCE (Frase)
**Definition:** Unit of text from space + capital letter to punctuation mark

**Identification:**
- Start: Space followed by capital letter
- End: Period (`.`), exclamation mark (`!`), question mark (`?`), or other punctuation

**Example:**
```
" This is a sentence."
" Another sentence!"
```

---

### SUBPARAGRAPH (Sotto-paragrafo)
**Definition:** Set of complex periods dependent on each other

**Identification:**
- Split by semicolons (`;`) and colons (`:`)
- Groups of related clauses

**Example:**
```
"This is the first part; this is the second part: and this is the third part."
```
Three subparagraphs in one paragraph.

---

### PARAGRAPH (Paragrafo)
**Definition:** Set of subparagraphs, typically separated by line breaks

**Identification:**
- Any non-empty paragraph in the document
- Separated by line breaks

**Example:**
```
This is paragraph 1.

This is paragraph 2.
```

---

### SECTION (Sezione)
**Definition:** Group of paragraphs, typically numbered or lettered

**Identification:**
- Start: Space + capital letter + period (e.g., " A. ", " B. ")
- End: Period followed by line break or empty paragraph

**Example:**
```
 A. Introduction
This is the introduction section.
It can span multiple paragraphs.

 B. Background
This is the background section.
```

---

## 🎨 Border Specifications

### Default Settings
- **Width:** 1/2 pt (0.5 points)
- **Color:** Black (#000000)
- **Style:** Solid line
- **Spacing:** 1 pt from text

### Visual Example
```
┌─────────────────────────┐
│  Bordered Section       │
│  with text content      │
└─────────────────────────┘
```

---

## 📝 Usage Examples

### Example 1: Border Only Sections

**Request:**
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

**Result:** Only sections (A., B., C., etc.) will have borders

---

### Example 2: Border All Paragraphs

**Request:**
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

**Result:** Every paragraph will have a border

---

### Example 3: Multiple Selections

**Request:**
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

**Result:** Both sections AND paragraphs will have borders (applied independently)

---

### Example 4: No Borders

**Request:**
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

**Result:** No borders applied, but file is still created with `edited_` prefix

---

## 🔄 Workflow

### Complete Workflow Diagram

```
┌──────────────┐
│ Upload Doc   │
│ POST /upload │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Extract Text │ (Optional)
│ POST /extract│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Apply Framing│
│ PUT /format  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Download     │
│ GET /download│
└──────────────┘
```

### Step-by-Step

1. **Upload Document**
   ```bash
   POST /api/documents/upload
   Content-Type: multipart/form-data
   Body: file=document.docx
   ```
   → Save `document_id` from response

2. **Apply Framing**
   ```bash
   PUT /api/documents/{document_id}/format
   Content-Type: application/json
   Body: { "framing": { "sections": true, ... } }
   ```
   → Returns `output_path` with edited file location

3. **Download Result**
   ```bash
   GET /api/documents/{document_id}/download
   ```
   → Downloads file with prefix `edited_`

---

## 💻 Code Examples

### Python (requests)

```python
import requests

# Upload document
with open('document.docx', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/documents/upload',
        files={'file': f}
    )
document_id = response.json()['document_id']

# Apply framing
framing_request = {
    "framing": {
        "sections": True,
        "paragraphs": False,
        "subparagraphs": False,
        "sentences": False
    }
}
response = requests.put(
    f'http://localhost:5000/api/documents/{document_id}/format',
    json=framing_request
)

# Download result
response = requests.get(
    f'http://localhost:5000/api/documents/{document_id}/download'
)
with open('edited_document.docx', 'wb') as f:
    f.write(response.content)
```

### TypeScript (Angular HttpClient)

```typescript
// Upload document
const formData = new FormData();
formData.append('file', file);

this.http.post<any>('/api/documents/upload', formData)
  .subscribe(response => {
    const documentId = response.document_id;
    
    // Apply framing
    const framingRequest = {
      framing: {
        sections: true,
        paragraphs: false,
        subparagraphs: false,
        sentences: false
      }
    };
    
    this.http.put<any>(`/api/documents/${documentId}/format`, framingRequest)
      .subscribe(result => {
        console.log('Framing applied:', result);
        
        // Download
        window.location.href = `/api/documents/${documentId}/download`;
      });
  });
```

### cURL

```bash
# Upload
curl -X POST http://localhost:5000/api/documents/upload \
  -F "file=@document.docx"

# Apply framing (replace {document_id})
curl -X PUT http://localhost:5000/api/documents/{document_id}/format \
  -H "Content-Type: application/json" \
  -d '{"framing":{"sections":true,"paragraphs":false,"subparagraphs":false,"sentences":false}}'

# Download
curl -X GET http://localhost:5000/api/documents/{document_id}/download \
  --output edited_document.docx
```

---

## 📊 Format Support

### DOCX (Microsoft Word)
✅ **Full Support**
- All framing options implemented
- Borders applied at paragraph level
- Native Word border formatting

### PDF
⚠️ **Limited Support**
- Basic implementation (page-level borders)
- TODO: Text block identification and precise borders

### TXT
❌ **Not Supported**
- Plain text files do not support formatting

---

## 🚨 Error Handling

### Common Errors

#### 400 Bad Request
```json
{
  "error": "ValidationException",
  "message": "'framing' field is required in request body",
  "status_code": 400
}
```
**Solution:** Ensure request body includes `"framing"` object

#### 404 Not Found
```json
{
  "error": "DocumentNotFoundException",
  "message": "Document not found",
  "status_code": 404
}
```
**Solution:** Use valid `document_id` from upload response

#### 500 Internal Server Error
```json
{
  "error": "FormattingException",
  "message": "Failed to apply framing: ...",
  "status_code": 500
}
```
**Solution:** Check document format and server logs

---

## ⚡ Performance Considerations

### Document Size
- **Small (<10 pages):** < 1 second
- **Medium (10-50 pages):** 1-3 seconds
- **Large (50+ pages):** 3-10 seconds

### Optimization Tips
1. Apply framing to specific parts only (not all)
2. Use batch processing for multiple documents
3. Consider async processing for very large documents

---

## 🔍 Advanced Features (Future)

### Customizable Borders
```json
{
  "framing": {
    "sections": true,
    "border_style": {
      "width": "1pt",
      "color": "#FF0000",
      "style": "dashed"
    }
  }
}
```

### AI-Powered Identification
Use Ollama to intelligently identify document parts:
```json
{
  "framing": {
    "use_ai": true,
    "sections": "auto"
  }
}
```

---

## 📚 Additional Resources

- **Implementation Guide:** `FRAMING_IMPLEMENTATION.md`
- **Quick Start Guide:** `QUICKSTART_FRAMING.md`
- **Test Collection:** `tests/integration/bruno/Divergentia/`
- **API Documentation:** `README.md`

---

## 🤝 Contributing

To extend the framing feature:

1. Add new identification logic in `formatting_service.py`
2. Update validation schema in `validators.py`
3. Add test cases in Bruno collection
4. Update documentation

---

## 📞 Support

For issues or questions:
- Check logs: `be/app.log`
- Review test collection: `tests/integration/bruno/Divergentia/README.md`
- See troubleshooting: `QUICKSTART_FRAMING.md`

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-10  
**Status:** ✅ Production Ready

