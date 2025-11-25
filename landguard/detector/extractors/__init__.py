"""
Extractor modules for various file formats.
"""

from detector.extractors.base import BaseExtractor
from detector.extractors.json_extractor import JSONExtractor
from detector.extractors.csv_extractor import CSVExtractor
from detector.extractors.pdf_extractor import PDFExtractor
from detector.extractors.ocr_extractor import OCRExtractor

__all__ = [
    'BaseExtractor',
    'JSONExtractor',
    'CSVExtractor',
    'PDFExtractor',
    'OCRExtractor'
]