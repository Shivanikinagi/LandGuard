"""
Detector module for file type detection and extraction.
"""

from detector.extractors import (
    BaseExtractor,
    JSONExtractor,
    CSVExtractor,
    PDFExtractor,
    OCRExtractor
)

__all__ = [
    'BaseExtractor',
    'JSONExtractor',
    'CSVExtractor',
    'PDFExtractor',
    'OCRExtractor'
]