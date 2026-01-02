"""
Anomaly Detection Agent
Autonomous agent for detecting fraud patterns in land documents
"""

import random
from typing import Dict, Any, List
from .base_agent import BaseAgent

class AnomalyDetectionAgent(BaseAgent):
    """Agent responsible for detecting anomalies in land documents"""
    
    def __init__(self):
        super().__init__(
            name="anomaly_detector",
            capabilities=["anomaly_detection", "fraud_analysis", "risk_scoring"]
        )
        self.anomaly_patterns = [
            "RAPID_TRANSFER",
            "PRICE_DISCREPANCY", 
            "OWNER_MISMATCH",
            "DOCUMENT_INCONSISTENCY",
            "VALUATION_ANOMALY"
        ]
        
    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect anomalies in land documents
        
        Args:
            task_data: Contains document information and metadata
            
        Returns:
            Dictionary with anomaly detection results
        """
        self.logger.info(f"Processing anomaly detection for {task_data.get('filename', 'unknown')}")
        
        # Simulate anomaly detection
        detected_anomalies = self._detect_anomalies(task_data)
        risk_score = self._calculate_risk_score(detected_anomalies)
        risk_level = self._determine_risk_level(risk_score)
        
        result = {
            "anomalies": detected_anomalies,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "confidence": round(random.uniform(0.7, 0.95), 2),
            "timestamp": self.created_at.isoformat()
        }
        
        self.log_task(task_data, result)
        return result
        
    def _detect_anomalies(self, task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect specific anomalies in documents"""
        anomalies = []
        
        # Randomly detect some anomalies for demo purposes
        for pattern in self.anomaly_patterns:
            if random.random() > 0.6:  # 40% chance of detecting each anomaly
                anomalies.append({
                    "type": pattern,
                    "description": self._get_anomaly_description(pattern),
                    "severity": random.choice(["LOW", "MEDIUM", "HIGH"]),
                    "confidence": round(random.uniform(0.6, 0.95), 2)
                })
                
        return anomalies
        
    def _get_anomaly_description(self, pattern: str) -> str:
        """Get human-readable description for anomaly pattern"""
        descriptions = {
            "RAPID_TRANSFER": "Property changed hands multiple times in short period",
            "PRICE_DISCREPANCY": "Sale price dropped significantly between transactions",
            "OWNER_MISMATCH": "Seller name inconsistent across documents",
            "DOCUMENT_INCONSISTENCY": "Document details don't match across records",
            "VALUATION_ANOMALY": "Property valuation inconsistent with market rates"
        }
        return descriptions.get(pattern, "Unknown anomaly detected")
        
    def _calculate_risk_score(self, anomalies: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score based on detected anomalies"""
        if not anomalies:
            return 1.0
            
        # Weighted scoring based on severity
        score = 0.0
        severity_weights = {"LOW": 1.0, "MEDIUM": 2.5, "HIGH": 4.0}
        
        for anomaly in anomalies:
            score += severity_weights.get(anomaly["severity"], 1.0) * anomaly["confidence"]
            
        # Normalize to 1-10 scale
        normalized_score = min(10.0, max(1.0, score))
        return round(normalized_score, 1)
        
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level label based on score"""
        if risk_score <= 3.0:
            return "LOW"
        elif risk_score <= 6.0:
            return "MEDIUM"
        elif risk_score <= 8.5:
            return "HIGH"
        else:
            return "CRITICAL"