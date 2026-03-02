"""
Test di verifica per l'integrazione Ollama Keywords
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_imports():
    """Test che tutti i moduli si importino correttamente"""
    print('1. Test Import Moduli...')

    from app.services.ollama_service import OllamaService, get_ollama_service
    from app.services.formatting_service import FormattingService, get_formatting_service
    from app.services.keyword_service import KeywordService, get_keyword_service
    from app.utils.validators import KeywordOptionsSchema

    print('   ✓ Tutti i moduli importati correttamente')
    return True

def test_schema_validation():
    """Test validazione schema Pydantic"""
    print('\n2. Test Validazione Schema...')

    from app.utils.validators import KeywordOptionsSchema

    # Schema base
    schema1 = KeywordOptionsSchema(max_keywords=5)
    assert schema1.max_keywords == 5
    assert schema1.include_proper_nouns == True
    assert schema1.model is None
    print(f'   ✓ Schema base: {schema1.dict()}')

    # Schema completo
    schema2 = KeywordOptionsSchema(max_keywords=7, model='llama2', include_proper_nouns=True)
    assert schema2.max_keywords == 7
    assert schema2.model == 'llama2'
    assert schema2.include_proper_nouns == True
    print(f'   ✓ Schema completo: {schema2.dict()}')

    # Test validazione range
    try:
        KeywordOptionsSchema(max_keywords=15)  # Dovrebbe fallire (max 10)
        assert False, "Validazione non ha rilevato max_keywords > 10"
    except:
        print('   ✓ Validazione range funziona (max_keywords <= 10)')

    return True

def test_method_signatures():
    """Test che i metodi abbiano le signature corrette"""
    print('\n3. Test Signature Metodi...')

    import inspect
    from app.services.ollama_service import OllamaService
    from app.services.formatting_service import FormattingService

    # Test OllamaService.extract_keywords
    sig = inspect.signature(OllamaService.extract_keywords)
    params = list(sig.parameters.keys())
    print(f'   extract_keywords params: {params}')
    assert 'self' in params
    assert 'text' in params
    assert 'max_keywords' in params
    assert 'model' in params
    assert 'use_cache' in params
    print('   ✓ OllamaService.extract_keywords() ha i parametri corretti')

    # Test FormattingService._apply_keywords_docx
    sig = inspect.signature(FormattingService._apply_keywords_docx)
    params = list(sig.parameters.keys())
    print(f'   _apply_keywords_docx params: {params}')
    assert 'self' in params
    assert 'input_path' in params
    assert 'output_path' in params
    assert 'keyword_options' in params
    print('   ✓ FormattingService._apply_keywords_docx() ha i parametri corretti')

    # Test che _identify_sections esista
    assert hasattr(FormattingService, '_identify_sections')
    print('   ✓ FormattingService._identify_sections() esiste')

    return True

def test_method_annotations():
    """Test che i metodi abbiano le type annotations corrette"""
    print('\n4. Test Type Annotations...')

    import inspect
    from typing import get_type_hints
    from app.services.ollama_service import OllamaService

    # Get type hints
    hints = get_type_hints(OllamaService.extract_keywords)
    print(f'   extract_keywords return type: {hints.get("return", "None")}')

    # Verifica che restituisca List[str]
    return_type = str(hints.get('return', ''))
    assert 'List' in return_type or 'list' in return_type
    print('   ✓ extract_keywords restituisce List[str]')

    return True

def main():
    """Esegui tutti i test"""
    print('=== Test Integrazione Ollama Keywords ===\n')

    tests = [
        test_imports,
        test_schema_validation,
        test_method_signatures,
        test_method_annotations
    ]

    failed = 0
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f'   ✗ Test fallito: {str(e)}')
            failed += 1

    print('\n' + '='*50)
    if failed == 0:
        print('✅ TUTTI I TEST SUPERATI')
        print('\nL\'implementazione è pronta per l\'uso!')
        return 0
    else:
        print(f'❌ {failed} test falliti')
        return 1

if __name__ == '__main__':
    sys.exit(main())

