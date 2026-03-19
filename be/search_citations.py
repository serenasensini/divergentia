"""
Search for citations in the entire document
"""
from docx import Document
import os

uploads_dir = "/home/ssensini/WebstormProjects/divergentia/be/uploads"
docs = [f for f in os.listdir(uploads_dir) if f.endswith('.docx')]

print(f"Searching {len(docs)} documents for citation fields...")
print("="*80)

for doc_name in docs[:3]:  # Check first 3 documents
    doc_path = os.path.join(uploads_dir, doc_name)
    print(f"\nDocument: {doc_name}")

    try:
        doc = Document(doc_path)
        found_fields = 0

        for i, para in enumerate(doc.paragraphs):
            for run in para.runs:
                if run._element is not None:
                    for child in run._element:
                        tag_name = str(child.tag)
                        if 'fldChar' in tag_name or 'instrText' in tag_name or 'fldData' in tag_name:
                            found_fields += 1
                            print(f"  Paragraph {i}: Field element found - {tag_name}")
                            print(f"    Run text: '{run.text[:80]}'")
                            if found_fields >= 5:  # Limit output
                                break
                    if found_fields >= 5:
                        break
            if found_fields >= 5:
                break

        if found_fields == 0:
            print(f"  No citation fields found")
        else:
            print(f"  Total fields found: {found_fields}+")

    except Exception as e:
        print(f"  Error reading document: {str(e)}")

print("\n" + "="*80)
print("Note: Even if no Open XML field elements are found, the new implementation")
print("preserves run structure, which is the key improvement.")

