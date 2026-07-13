"""OCR package.

PaddleOCR is imported lazily only when a scan requires recognition. This keeps
text-layer PDF conversion available even on machines where OCR is not yet
installed.
"""
