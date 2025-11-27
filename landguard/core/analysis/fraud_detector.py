"""
Fraud Detection Module
Detects fraudulent patterns in land documents
"""

import re
from typing import Dict, List, Any


class FraudDetector:
    """Fraud detection for land documents"""
    
    def __init__(self):
        """Initialize fraud detector"""
        self.fraud_patterns = [
            r"fake",
            r"forged",
            r"counterfeit",
            r"fraudulent",
            r"tampered"
        ]
        
    def detect_fraud(self, document_text: str) -> Dict[str, Any]:
        """
        Detect fraud in document text
        
        Args:
            document_text: Document text to analyze
            
        Returns:
            Dictionary with fraud detection results
        """
        indicators = []
        fraud_score = 0.0
        
        # Check for fraud patterns
        for pattern in self.fraud_patterns:
            matches = re.findall(pattern, document_text.lower())
            if matches:
                indicators.append({
                    "pattern": pattern,
                    "matches": len(matches),
                    "severity": "high"
                })
                fraud_score += 0.2
        
        # Check for suspicious formatting
        if self._check_suspicious_formatting(document_text):
            indicators.append({
                "type": "suspicious_formatting",
                "severity": "medium"
            })
            fraud_score += 0.1
        
        # Check for inconsistent dates
        if self._check_inconsistent_dates(document_text):
            indicators.append({
                "type": "inconsistent_dates",
                "severity": "high"
            })
            fraud_score += 0.3
        
        # Normalize fraud score
        fraud_score = min(fraud_score, 1.0)
        
        return {
            "fraud_detected": fraud_score > 0.3,
            "fraud_score": fraud_score,
            "indicators": indicators,
            "confidence": 0.8 if indicators else 0.95
        }
    
    def _check_suspicious_formatting(self, text: str) -> bool:
        """Check for suspicious formatting patterns"""
        # Check for excessive whitespace
        if re.search(r'\s{10,}', text):
            return True
        
        # Check for unusual character repetition
        if re.search(r'(.)\1{5,}', text):
            return True
        
        return False
    
    def _check_inconsistent_dates(self, text: str) -> bool:
        """Check for inconsistent date patterns"""
        # Extract dates (simplified)
        dates = re.findall(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', text)
        
        # Basic check for future dates (placeholder)
        # In production, this would be more sophisticated
        return len(dates) > 0 and any('2030' in date or '2040' in date for date in dates)