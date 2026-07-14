"""Advanced font detection and VNI-Windows encoding analysis."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from src.core.logger import log


@dataclass(slots=True)
class FontMetadata:
    """Font information extracted from PDF text."""
    name: str
    size: float
    is_vni_windows: bool
    confidence: float
    encoding_type: str  # 'unicode', 'vni_windows', 'mixed', 'unknown'


class FontDetector:
    """Detect and analyze font encoding issues in PDF text."""

    # VNI-Windows specific character patterns
    VNI_PATTERNS = {
        'horn_vowels': r'[ơư][øùûï]',  # ơø, ơù, ưù, etc.
        'combining_marks': r'[\xd0-\xd2]',  # Special combining marks
        'accented_sequences': r'[a-z][øùûïõ]',  # a + tone mark combinations
        'system_errors': r'[c@#][0-9a-f]{1,3}',  # Character code sequences like c6, @1a
    }

    UNICODE_PATTERNS = {
        'vietnamese': r'[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]',
        'combining': r'[\u0300-\u036f]',  # Unicode combining diacriticals
    }

    def __init__(self):
        """Initialize font detector with pattern compilation."""
        self._compiled_vni_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.VNI_PATTERNS.items()
        }
        self._compiled_unicode_patterns = {
            name: re.compile(pattern)
            for name, pattern in self.UNICODE_PATTERNS.items()
        }

    def analyze_text(self, text: str, font_name: str = "", font_size: float = 0) -> FontMetadata:
        """
        Analyze text for encoding issues and return metadata.

        Args:
            text: The text to analyze
            font_name: The declared font name from PDF
            font_size: The font size from PDF

        Returns:
            FontMetadata with encoding analysis
        """
        if not text or len(text.strip()) == 0:
            return FontMetadata(
                name=font_name or "Unknown",
                size=font_size,
                is_vni_windows=False,
                confidence=0.0,
                encoding_type="unknown"
            )

        vni_score = self._detect_vni_windows(text)
        unicode_score = self._detect_unicode(text)

        # Determine encoding type
        if vni_score > unicode_score and vni_score > 0.3:
            encoding_type = "vni_windows"
            confidence = vni_score
        elif unicode_score > 0.5:
            encoding_type = "unicode"
            confidence = unicode_score
        elif vni_score > 0.1:
            encoding_type = "mixed"
            confidence = max(vni_score, unicode_score)
        else:
            encoding_type = "unknown"
            confidence = 0.0

        return FontMetadata(
            name=font_name or "Unknown",
            size=font_size,
            is_vni_windows=encoding_type in ("vni_windows", "mixed"),
            confidence=confidence,
            encoding_type=encoding_type
        )

    def _detect_vni_windows(self, text: str) -> float:
        """Calculate VNI-Windows likelihood score (0.0 to 1.0)."""
        if not text:
            return 0.0

        evidence_count = 0
        total_checks = 0

        # Check for VNI-specific patterns
        for pattern_name, pattern in self._compiled_vni_patterns.items():
            matches = len(pattern.findall(text))
            if matches > 0:
                evidence_count += 1
            total_checks += 1

        # Strong indicator: multi-character sequences
        for marker in ['AØ', 'AÙ', 'aø', 'aù', 'ơø', 'ưù']:
            if marker in text:
                evidence_count += 2

        # System error patterns (like 'c6' for 'có')
        if re.search(self.VNI_PATTERNS['system_errors'], text):
            evidence_count += 1.5

        text_length = len(text)
        score = min(1.0, evidence_count / (total_checks + text_length / 100))
        return score

    def _detect_unicode(self, text: str) -> float:
        """Calculate Unicode likelihood score (0.0 to 1.0)."""
        if not text:
            return 0.0

        # Count Vietnamese Unicode characters
        vietnamese_chars = len(self._compiled_unicode_patterns['vietnamese'].findall(text))
        combining_marks = len(self._compiled_unicode_patterns['combining'].findall(text))

        total_chars = len([c for c in text if c.isalpha()])
        if total_chars == 0:
            return 0.0

        score = (vietnamese_chars + combining_marks) / total_chars
        return min(1.0, score)

    def get_font_issues(self, text: str, font_name: str = "") -> dict:
        """
        Identify specific font encoding issues.

        Returns dict with keys like 'vni_sequences', 'mixed_encoding', etc.
        """
        issues = {}

        # Check for VNI sequences
        vni_sequences = []
        for marker in ['AØ', 'AÙ', 'aø', 'aù', 'ơø', 'ưù']:
            if marker in text:
                vni_sequences.append(marker)
        if vni_sequences:
            issues['vni_sequences'] = list(set(vni_sequences))

        # Check for system errors
        system_errors = re.findall(self.VNI_PATTERNS['system_errors'], text)
        if system_errors:
            issues['system_error_codes'] = system_errors[:5]  # First 5 occurrences

        # Check for mixed encoding
        vni_score = self._detect_vni_windows(text)
        unicode_score = self._detect_unicode(text)
        if vni_score > 0.1 and unicode_score > 0.1:
            issues['mixed_encoding'] = True

        # Font mismatch detection
        if font_name and vni_score > 0.3:
            if 'Times' in font_name or 'Arial' in font_name:
                issues['font_mismatch'] = f"Font '{font_name}' may not display VNI correctly"

        return issues
