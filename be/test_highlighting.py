"""
Test script for part-of-speech highlighting feature
"""
import unittest
from app.services.keyword_service import get_keyword_service


class TestPOSIdentification(unittest.TestCase):
    """Test part-of-speech identification functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.keyword_service = get_keyword_service()

    def test_analyze_pos(self):
        """Test analyze_pos function"""
        text = "Il gatto veloce mangia lentamente."
        tokens = self.keyword_service.analyze_pos(text)

        self.assertIsInstance(tokens, list)
        self.assertGreater(len(tokens), 0)

        # Check that tokens have the required keys
        for token in tokens:
            self.assertIn('text', token)
            self.assertIn('pos', token)
            self.assertIn('lemma', token)
            self.assertIn('is_stop', token)
            self.assertIn('is_punct', token)
            self.assertIn('is_space', token)

        print(f"✓ analyze_pos test passed - Found {len(tokens)} tokens")

    def test_is_noun(self):
        """Test is_noun function"""
        # Test nouns
        self.assertTrue(self.keyword_service.is_noun("gatto"))
        self.assertTrue(self.keyword_service.is_noun("casa"))
        self.assertTrue(self.keyword_service.is_noun("libro"))

        # Test non-nouns
        self.assertFalse(self.keyword_service.is_noun("veloce"))  # adjective
        self.assertFalse(self.keyword_service.is_noun("mangia"))  # verb

        print("✓ is_noun test passed")

    def test_is_verb(self):
        """Test is_verb function"""
        # Test verbs
        self.assertTrue(self.keyword_service.is_verb("mangia"))
        self.assertTrue(self.keyword_service.is_verb("corre"))
        self.assertTrue(self.keyword_service.is_verb("scrive"))

        # Test non-verbs
        self.assertFalse(self.keyword_service.is_verb("gatto"))  # noun
        self.assertFalse(self.keyword_service.is_verb("veloce"))  # adjective

        print("✓ is_verb test passed")

    def test_is_adjective(self):
        """Test is_adjective function"""
        # Test adjectives
        self.assertTrue(self.keyword_service.is_adjective("veloce"))
        self.assertTrue(self.keyword_service.is_adjective("bello"))
        self.assertTrue(self.keyword_service.is_adjective("grande"))

        # Test non-adjectives
        self.assertFalse(self.keyword_service.is_adjective("gatto"))  # noun
        self.assertFalse(self.keyword_service.is_adjective("mangia"))  # verb

        print("✓ is_adjective test passed")

    def test_is_adverb(self):
        """Test is_adverb function"""
        # Test adverbs
        self.assertTrue(self.keyword_service.is_adverb("lentamente"))
        self.assertTrue(self.keyword_service.is_adverb("velocemente"))
        self.assertTrue(self.keyword_service.is_adverb("bene"))

        # Test non-adverbs
        self.assertFalse(self.keyword_service.is_adverb("gatto"))  # noun
        self.assertFalse(self.keyword_service.is_adverb("veloce"))  # adjective

        print("✓ is_adverb test passed")

    def test_empty_input(self):
        """Test with empty input"""
        self.assertEqual(self.keyword_service.analyze_pos(""), [])
        self.assertEqual(self.keyword_service.analyze_pos("   "), [])

        self.assertFalse(self.keyword_service.is_noun(""))
        self.assertFalse(self.keyword_service.is_verb(""))
        self.assertFalse(self.keyword_service.is_adjective(""))
        self.assertFalse(self.keyword_service.is_adverb(""))

        print("✓ Empty input test passed")


class TestHighlightingSchema(unittest.TestCase):
    """Test highlighting schema validation"""

    def test_highlighting_schema_validation(self):
        """Test HighlightingOptionsSchema validation"""
        from app.utils.validators import HighlightingOptionsSchema, validate_schema

        # Test valid data
        valid_data = {
            'enabled': True,
            'color': '#FFFF00',
            'nouns': True,
            'verbs': False,
            'adjectives': False,
            'adverbs': False
        }

        schema = validate_schema(HighlightingOptionsSchema, valid_data)
        self.assertEqual(schema.enabled, True)
        self.assertEqual(schema.color, '#FFFF00')
        self.assertEqual(schema.nouns, True)

        print("✓ Schema validation test passed")

    def test_color_validation(self):
        """Test color format validation"""
        from app.utils.validators import HighlightingOptionsSchema, validate_schema

        # Test with # prefix
        data1 = {'enabled': True, 'color': '#FF0000', 'nouns': True}
        schema1 = validate_schema(HighlightingOptionsSchema, data1)
        self.assertEqual(schema1.color, '#FF0000')

        # Test without # prefix
        data2 = {'enabled': True, 'color': 'FF0000', 'nouns': True}
        schema2 = validate_schema(HighlightingOptionsSchema, data2)
        self.assertEqual(schema2.color, '#FF0000')

        print("✓ Color validation test passed")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Testing Part-of-Speech Highlighting Feature")
    print("="*60 + "\n")

    unittest.main(verbosity=2)

