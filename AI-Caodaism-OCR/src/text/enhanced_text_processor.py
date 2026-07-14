"""Enhanced text processor with AI-powered correction pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from src.core.logger import log
from src.ocr.llm_corrector import LLMCorrector
from src.text.font_detector import FontDetector
from src.core.vietnamese_encoding import to_unicode, is_vni_windows


class EnhancedTextProcessor:
    """
    Advanced text processing pipeline:
    1. Detect font encoding (VNI, Unicode, mixed)
    2. Convert VNI-Windows to Unicode
    3. Apply AI-powered spell correction with context awareness
    4. Preserve formatting and images
    """

    def __init__(self, enable_ai_correction: bool = True, ai_api_key: Optional[str] = None):
        """
        Initialize enhanced text processor.

        Args:
            enable_ai_correction: Whether to use AI for text correction
            ai_api_key: Optional API key for LLM (uses env var if not provided)
        """
        self.font_detector = FontDetector()
        self.llm_corrector = LLMCorrector(api_key=ai_api_key) if enable_ai_correction else None
        log.info("✅ Enhanced Text Processor initialized (AI correction: %s)", enable_ai_correction)

    def process_text(self, text: str, font_name: str = "", font_size: float = 0) -> str:
        """
        Process text through full pipeline: detect encoding → convert → correct.

        Args:
            text: Raw text from PDF
            font_name: Font name from PDF metadata
            font_size: Font size from PDF metadata

        Returns:
            Fully processed Unicode text
        """
        if not text or not text.strip():
            return text

        # Step 1: Analyze font encoding
        metadata = self.font_detector.analyze_text(text, font_name, font_size)
        issues = self.font_detector.get_font_issues(text, font_name)

        log.info(
            "📊 Text Analysis: encoding=%s, confidence=%.1f%%, issues=%s",
            metadata.encoding_type,
            metadata.confidence * 100,
            list(issues.keys())
        )

        # Step 2: Convert VNI-Windows to Unicode
        if metadata.is_vni_windows:
            text = self._convert_vni_to_unicode(text)
            log.info("🔄 Converted VNI-Windows to Unicode")

        # Step 3: Apply AI-powered correction if enabled and text has issues
        if self.llm_corrector and self._should_apply_correction(metadata, issues):
            text = self._apply_ai_correction(text, font_name)
            log.info("✨ Applied AI-powered correction")

        return text

    def process_blocks(self, blocks: list) -> list:
        """
        Process text blocks from PDF (preserves structure).

        Args:
            blocks: List of ContentBlock objects from PDFProcessor

        Returns:
            List of blocks with corrected text
        """
        from src.pdf.pdf_processor import ContentBlock

        processed_blocks = []
        for block in blocks:
            if block.kind == "text":
                # Process each text span
                for span in block.spans:
                    span.text = self.process_text(span.text)
                processed_blocks.append(block)
            else:
                # Keep image blocks as-is
                processed_blocks.append(block)

        return processed_blocks

    def _convert_vni_to_unicode(self, text: str) -> str:
        """Convert VNI-Windows encoded text to proper Unicode."""
        return to_unicode(text)

    def _should_apply_correction(self, metadata, issues: dict) -> bool:
        """Decide whether to apply AI correction based on analysis."""
        # Apply if high confidence of problems
        if metadata.encoding_type in ("vni_windows", "mixed"):
            return True

        if 'system_error_codes' in issues:
            return True

        if 'mixed_encoding' in issues:
            return True

        return False

    def _apply_ai_correction(self, text: str, font_name: str = "") -> str:
        """
        Apply LLM-based spell correction with context awareness.

        Args:
            text: Text to correct
            font_name: Font name for context

        Returns:
            Corrected text
        """
        if not self.llm_corrector or not self.llm_corrector.model:
            log.warning("⚠ LLM corrector not available, skipping AI correction")
            return text

        context_hint = "Tài liệu, kinh sách, nội san thuộc tôn giáo Cao Đài"
        if "kinh" in text.lower() or "cao đài" in text.lower():
            context_hint = "Tài liệu tôn giáo Cao Đài, gồm các kinh sách cổ"

        try:
            corrected = self.llm_corrector.correct_text(text, context_hint)
            return corrected
        except Exception as e:
            log.error("❌ AI correction failed: %s. Returning original text.", e)
            return text

    def get_processing_report(self, text: str, font_name: str = "") -> dict:
        """
        Generate detailed report about text processing.

        Args:
            text: Text to analyze
            font_name: Font name

        Returns:
            Dictionary with analysis report
        """
        metadata = self.font_detector.analyze_text(text, font_name)
        issues = self.font_detector.get_font_issues(text, font_name)

        report = {
            "original_length": len(text),
            "encoding_type": metadata.encoding_type,
            "confidence": f"{metadata.confidence:.1%}",
            "is_vni_windows": metadata.is_vni_windows,
            "issues": issues,
            "requires_correction": self._should_apply_correction(metadata, issues),
            "font_name": metadata.name,
            "font_size": metadata.size,
        }

        return report
