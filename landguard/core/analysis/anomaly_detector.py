"""
Anomaly Detection Module
Detects anomalies and irregularities in land documents
"""

import re
from typing import Dict, List, Any


class AnomalyDetector:
    """Anomaly detection for land documents"""
    
    def __init__(self):
        """Initialize anomaly detector"""
        self.min_document_length = 100
        self.max_document_length = 50000
        
    def detect_anomalies(self, document_text: str) -> Dict[str, Any]:
        """
        Detect anomalies in document text
        
        Args:
            document_text: Document text to analyze
            
        Returns:
            Dictionary with anomaly detection results
        """
        anomaly_types = []
        anomaly_score = 0.0
        
        # Check document length
        if len(document_text) < self.min_document_length:
            anomaly_types.append({
                "type": "document_too_short",
                "severity": "medium",
                "details": f"Document length: {len(document_text)} characters"
            })
            anomaly_score += 0.2
        
        if len(document_text) > self.max_document_length:
            anomaly_types.append({
                "type": "document_too_long",
                "severity": "low",
                "details": f"Document length: {len(document_text)} characters"
            })
            anomaly_score += 0.1
        
        # Check for missing required fields
        missing_fields = self._check_missing_fields(document_text)
        if missing_fields:
            anomaly_types.append({
                "type": "missing_fields",
                "severity": "high",
                "details": f"Missing: {', '.join(missing_fields)}"
            })
            anomaly_score += 0.3
        
        # Check for unusual characters
        if self._check_unusual_characters(document_text):
            anomaly_types.append({
                "type": "unusual_characters",
                "severity": "medium"
            })
            anomaly_score += 0.15
        
        # Check for duplicate content
        if self._check_duplicate_content(document_text):
            anomaly_types.append({
                "type": "duplicate_content",
                "severity": "low"
            })
            anomaly_score += 0.1
        
        # Normalize anomaly score
        anomaly_score = min(anomaly_score, 1.0)
        
        return {
            "anomaly_detected": anomaly_score > 0.2,
            "anomaly_score": anomaly_score,
            "anomaly_types": anomaly_types,
            "confidence": 0.75 if anomaly_types else 0.9
        }
    
    def _check_missing_fields(self, text: str) -> List[str]:
        """Check for missing required fields"""
        missing = []
        
        required_patterns = {
            "owner": r"owner|proprietor|name",
            "location": r"location|address|situated",
            "area": r"area|measurement|square",
            "date": r"date|dated"
        }
        
        for field, pattern in required_patterns.items():
            if not re.search(pattern, text.lower()):
                missing.append(field)
        
        return missing
    
    def _check_unusual_characters(self, text: str) -> bool:
        """Check for unusual or non-printable characters"""
        # Check for excessive special characters
        special_chars = re.findall(r'[^a-zA-Z0-9\s\.,;:\-()]', text)
        
        # If more than 5% of characters are special, flag as unusual
        return len(special_chars) / len(text) > 0.05 if text else False
    
    def _check_duplicate_content(self, text: str) -> bool:
        """Check for duplicate content patterns"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Check for duplicate sentences
        unique_sentences = set(s.strip().lower() for s in sentences if s.strip())
        
        # If more than 20% duplication, flag it
        if len(sentences) > 0:
            duplication_ratio = 1 - (len(unique_sentences) / len(sentences))
            return duplication_ratio > 0.2
        
        return False