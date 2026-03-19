"""
Test script to verify that citations and references are preserved in their original position
after applying part-of-speech highlighting
"""
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from docx import Document
from docx.shared import RGBColor
from app.services.formatting_service import FormattingService


def analyze_document_structure(doc_path, title="Document"):
    """Analyze and print document structure showing runs and complex fields"""
    doc = Document(doc_path)

    print(f"\n{'='*80}")
    print(f"{title}: {doc_path}")
    print(f"{'='*80}")

    for i, para in enumerate(doc.paragraphs[:10]):  # First 10 paragraphs
        if not para.text.strip():
            continue

        print(f"\nParagraph {i}: {para.text[:100]}...")
        print(f"  Runs: {len(para.runs)}")

        for j, run in enumerate(para.runs):
            run_text = run.text

            # Check for complex fields
            has_field = False
            field_types = []
            if run._element is not None:
                for child in run._element:
                    tag_name = child.tag
                    if 'fldChar' in tag_name:
                        field_types.append('fldChar')
                        has_field = True
                    elif 'instrText' in tag_name:
                        field_types.append('instrText')
                        has_field = True
                    elif 'fldData' in tag_name:
                        field_types.append('fldData')
                        has_field = True

            field_marker = f" [FIELD: {','.join(field_types)}]" if has_field else ""
            color_info = ""
            if run.font.color.rgb:
                color_info = f" (color: {run.font.color.rgb})"

            print(f"    Run {j}: '{run_text[:50]}'{field_marker}{color_info}")


def test_citations_preservation():
    """Test that citations and references remain in their original position"""

    print("\n" + "="*80)
    print("TESTING CITATIONS AND REFERENCES PRESERVATION")
    print("="*80)

    # Use one of the uploaded documents
    test_doc_path = "/home/ssensini/WebstormProjects/divergentia/be/uploads/ELABORATO_TESI_0fe8354b.docx"

    if not os.path.exists(test_doc_path):
        print(f"Test document not found: {test_doc_path}")
        print("Searching for available test documents...")
        uploads_dir = "/home/ssensini/WebstormProjects/divergentia/be/uploads"
        if os.path.exists(uploads_dir):
            docs = [f for f in os.listdir(uploads_dir) if f.endswith('.docx')]
            if docs:
                test_doc_path = os.path.join(uploads_dir, docs[0])
                print(f"Using: {test_doc_path}")
            else:
                print("No test documents found. Skipping test.")
                return
        else:
            print("Uploads directory not found. Skipping test.")
            return

    # Analyze original document
    analyze_document_structure(test_doc_path, "ORIGINAL DOCUMENT")

    # Apply highlighting with nouns formatting
    output_path = "/home/ssensini/WebstormProjects/divergentia/be/outputs/test_citations_preservation.docx"

    highlighting_options = {
        'enabled': True,
        'color': '#FF0000',  # Red
        'style': 'bold',
        'font_size': None,
        'font_family': None,
        'nouns': True,
        'verbs': False,
        'adjectives': False,
        'adverbs': False
    }

    print("\nApplying part-of-speech highlighting...")
    formatting_service = FormattingService()

    try:
        result = formatting_service.apply_highlighting(
            test_doc_path,
            output_path,
            highlighting_options
        )

        print(f"✓ Highlighting applied successfully")
        print(f"  Words formatted: {result['words_formatted']}")
        print(f"  Paragraphs processed: {result['paragraphs_processed']}")
        print(f"  Output: {output_path}")

        # Analyze output document
        analyze_document_structure(output_path, "OUTPUT DOCUMENT (AFTER HIGHLIGHTING)")

        print("\n" + "="*80)
        print("TEST COMPLETE")
        print("="*80)
        print("\nPlease manually verify that:")
        print("1. Citations/references remain in their original positions")
        print("2. Citations/references maintain their original formatting (e.g., purple color)")
        print("3. Nouns are correctly formatted in red and bold")
        print("4. Non-noun text maintains its original formatting")

    except Exception as e:
        print(f"✗ Error during highlighting: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_citations_preservation()

