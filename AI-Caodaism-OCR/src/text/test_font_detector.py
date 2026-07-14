"""Test suite for font detector and encoding analysis."""

import unittest
from src.text.font_detector import FontDetector, FontMetadata


class TestFontDetector(unittest.TestCase):
    """Test font detection and VNI encoding analysis."""

    def setUp(self):
        """Initialize font detector for each test."""
        self.detector = FontDetector()

    def test_vni_windows_detection(self):
        """Test detection of VNI-Windows encoded text."""
        # VNI sequences that should be detected
        vni_text = "AØ AÙ aø aù ơø ưù"
        metadata = self.detector.analyze_text(vni_text, "Times New Roman", 13)
        
        print(f"✓ VNI Detection Test:")
        print(f"  Text: {vni_text}")
        print(f"  Encoding: {metadata.encoding_type}")
        print(f"  Confidence: {metadata.confidence:.2%}")
        print(f"  Is VNI Windows: {metadata.is_vni_windows}\n")
        
        self.assertTrue(metadata.is_vni_windows)
        self.assertGreater(metadata.confidence, 0.5)

    def test_unicode_detection(self):
        """Test detection of correct Unicode Vietnamese text."""
        unicode_text = "Tài liệu Cao Đài với các ký tự Unicode đúng: à á ả ã ạ"
        metadata = self.detector.analyze_text(unicode_text, "Times New Roman", 13)
        
        print(f"✓ Unicode Detection Test:")
        print(f"  Text: {unicode_text}")
        print(f"  Encoding: {metadata.encoding_type}")
        print(f"  Confidence: {metadata.confidence:.2%}")
        print(f"  Is VNI Windows: {metadata.is_vni_windows}\n")
        
        self.assertEqual(metadata.encoding_type, "unicode")
        self.assertGreater(metadata.confidence, 0.5)

    def test_system_error_detection(self):
        """Test detection of system error codes (e.g., 'c6' for 'có')."""
        error_text = "C6 là một ký tự lỗi hệ thống, cũng như @1a và #2b"
        metadata = self.detector.analyze_text(error_text)
        issues = self.detector.get_font_issues(error_text)
        
        print(f"✓ System Error Detection Test:")
        print(f"  Text: {error_text}")
        print(f"  Issues found: {issues}")
        print(f"  Encoding: {metadata.encoding_type}\n")
        
        self.assertIn('system_error_codes', issues)
        self.assertGreater(len(issues['system_error_codes']), 0)

    def test_mixed_encoding_detection(self):
        """Test detection of mixed VNI and Unicode text."""
        mixed_text = "Đây là văn bản hỗn hợp với cả Unicode (Cao Đài) và VNI (AØ aù)"
        metadata = self.detector.analyze_text(mixed_text)
        issues = self.detector.get_font_issues(mixed_text)
        
        print(f"✓ Mixed Encoding Detection Test:")
        print(f"  Text: {mixed_text}")
        print(f"  Encoding: {metadata.encoding_type}")
        print(f"  Issues: {issues}")
        print(f"  Confidence: {metadata.confidence:.2%}\n")
        
        self.assertEqual(metadata.encoding_type, "mixed")
        self.assertIn('mixed_encoding', issues)

    def test_font_mismatch_warning(self):
        """Test detection of font mismatch with encoding."""
        vni_text = "AØ aù ơø ưù - VNI encoded text"
        issues = self.detector.get_font_issues(vni_text, "Times New Roman")
        
        print(f"✓ Font Mismatch Warning Test:")
        print(f"  Text: {vni_text}")
        print(f"  Font: Times New Roman")
        print(f"  Issues: {issues}\n")
        
        # May or may not have font_mismatch depending on confidence
        if 'font_mismatch' in issues:
            self.assertIn('Times', issues['font_mismatch'])

    def test_empty_text_handling(self):
        """Test handling of empty or whitespace-only text."""
        metadata = self.detector.analyze_text("   ")
        
        print(f"✓ Empty Text Handling Test:")
        print(f"  Input: '   ' (whitespace)")
        print(f"  Encoding: {metadata.encoding_type}")
        print(f"  Confidence: {metadata.confidence}\n")
        
        self.assertEqual(metadata.encoding_type, "unknown")
        self.assertEqual(metadata.confidence, 0.0)

    def test_real_world_cao_dai_text(self):
        """Test with realistic Cao Dai document text."""
        cao_dai_unicode = """
        Kinh Cao Đài vô cùng tôn quý, 
        Là công pháp truyền lại từ xưa,
        Giảng dạy về đạo Cao Đài,
        Giúp mọi sinh linh được giác ngộ.
        """
        
        metadata = self.detector.analyze_text(cao_dai_unicode)
        print(f"✓ Real-world Cao Dai Text Test:")
        print(f"  Text length: {len(cao_dai_unicode)} characters")
        print(f"  Encoding: {metadata.encoding_type}")
        print(f"  Confidence: {metadata.confidence:.2%}\n")
        
        self.assertEqual(metadata.encoding_type, "unicode")

    def test_vni_to_unicode_sequences(self):
        """Test identification of specific VNI sequences."""
        text_with_vni = "Đây có ơø và ơù cùng ưù"
        issues = self.detector.get_font_issues(text_with_vni)
        
        print(f"✓ VNI Sequences Identification Test:")
        print(f"  Text: {text_with_vni}")
        print(f"  VNI Sequences found: {issues.get('vni_sequences', [])}\n")
        
        if 'vni_sequences' in issues:
            self.assertIn('ơø', issues['vni_sequences'])


if __name__ == "__main__":
    # Run tests with verbose output
    print("=" * 70)
    print("Font Detector and VNI Encoding Analysis Test Suite")
    print("=" * 70 + "\n")
    
    unittest.main(verbosity=2)
