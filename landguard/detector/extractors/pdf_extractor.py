"""
PDF file extractor for land records.
"""

import re
from typing import Dict, Any, List
from pathlib import Path

try:
    from pdfminer.high_level import extract_text
    HAS_PDFMINER = True
except ImportError:
    HAS_PDFMINER = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

from core.models import LandRecord, OwnerHistory, Transaction
from detector.extractors.base import BaseExtractor


class PDFExtractor(BaseExtractor):
    """Extract land records from PDF files."""
    
    def extract(self, file_path: str) -> Dict[str, Any]:
        """
        Extract data from PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted land record data
        """
        # Extract text
        text = self._extract_text(file_path)
        
        # Parse the text
        return self._parse_text(text)
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF using available library."""
        
        if HAS_PDFMINER:
            try:
                return extract_text(file_path)
            except Exception as e:
                print(f"PDFMiner failed: {e}")
        
        if HAS_PYPDF2:
            try:
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    return text
            except Exception as e:
                print(f"PyPDF2 failed: {e}")
        
        raise ValueError("No PDF extraction library available")
    
    def _parse_text(self, text: str) -> Dict[str, Any]:
        """Parse extracted text to find land record fields."""
        
        result = {
            'land_id': self._extract_land_id(text),
            'owner_history': self._extract_owners(text),
            'transactions': self._extract_transactions(text),
            'property_area': self._extract_property_area(text),
            'registration_number': self._extract_registration_number(text),
            'raw_text': text,
            'extraction_confidence': 0.7
        }
        
        return result
    
    def _extract_land_id(self, text: str) -> str:
        """Extract land ID from text."""
        patterns = [
            r'Land\s*ID[:\s]+([A-Z0-9-]+)',
            r'Property\s*ID[:\s]+([A-Z0-9-]+)',
            r'Parcel[:\s]+([A-Z0-9-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "UNKNOWN"
    
    def _extract_owners(self, text: str) -> List[Dict[str, Any]]:
        """Extract owner history from text."""
        owners = []
        
        # Look for owner patterns
        owner_pattern = r'Owner[:\s]+([A-Za-z\s]+?)(?:\n|Date|$)'
        matches = re.finditer(owner_pattern, text, re.IGNORECASE)
        
        for match in matches:
            owner_name = match.group(1).strip()
            if owner_name:
                owners.append({
                    'owner_name': owner_name,
                    'date': None
                })
        
        return owners if owners else [{'owner_name': 'UNKNOWN'}]
    
    def _extract_transactions(self, text: str) -> List[Dict[str, Any]]:
        """Extract transactions from text."""
        transactions = []
        
        # Look for transaction patterns
        tx_pattern = r'Transaction[:\s]+([A-Z0-9-]+)'
        matches = re.finditer(tx_pattern, text, re.IGNORECASE)
        
        for match in matches:
            tx_id = match.group(1).strip()
            transactions.append({
                'tx_id': tx_id,
                'amount': None,
                'from_party': None,
                'to_party': None
            })
        
        return transactions
    
    def _extract_property_area(self, text: str) -> float | None:
        """Extract property area from text."""
        patterns = [
            r'Area[:\s]+([\d,]+\.?\d*)\s*(?:sq|sqm|m2)',
            r'Size[:\s]+([\d,]+\.?\d*)\s*(?:sq|sqm|m2)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except:
                    pass
        
        return None
    
    def _extract_registration_number(self, text: str) -> str | None:
        """Extract registration number from text."""
        pattern = r'Registration[:\s]+([A-Z0-9-]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(1)
        
        return None