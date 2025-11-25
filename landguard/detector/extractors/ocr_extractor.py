"""
OCR extractor for scanned images of land records.
"""

from typing import Dict, Any
from pathlib import Path

try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

from detector.extractors.pdf_extractor import PDFExtractor
from detector.extractors.base import BaseExtractor


class OCRExtractor(BaseExtractor):
    """Extract land records from images using OCR."""
    
    def __init__(self):
        super().__init__()
        self.pdf_extractor = PDFExtractor()
    
    def extract(self, file_path: str) -> Dict[str, Any]:
        """
        Extract data from image file using OCR.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Dictionary containing extracted land record data
        """
        if not HAS_OCR:
            raise ValueError(
                "OCR libraries not installed. "
                "Install with: pip install pytesseract Pillow"
            )
        
        try:
            # Load and preprocess image
            image = Image.open(file_path)
            
            # Convert to grayscale for better OCR
            if image.mode != 'L':
                image = image.convert('L')
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            # Use PDF extractor's text parsing logic
            return self.pdf_extractor._parse_text(text)
            
        except Exception as e:
            raise ValueError(f"OCR extraction failed: {e}")