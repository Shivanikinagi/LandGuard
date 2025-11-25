"""
JSON file extractor for land records.
"""

import json
from typing import Dict, Any
from pathlib import Path

from core.models import LandRecord, OwnerHistory, Transaction
from detector.extractors.base import BaseExtractor


class JSONExtractor(BaseExtractor):
    """Extract land records from JSON files."""
    
    def extract(self, file_path: str) -> Dict[str, Any]:
        """
        Extract data from JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dictionary containing extracted land record data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # If it's a list, take the first element
            if isinstance(data, list):
                if len(data) > 0:
                    data = data[0]
                else:
                    raise ValueError("Empty JSON array")
            
            # Normalize the data structure
            normalized = self._normalize_json(data)
            
            return normalized
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Failed to extract JSON: {e}")
    
    def _normalize_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize JSON structure to match LandRecord model."""
        
        # Handle owner_history
        if 'owner_history' in data:
            owner_history = []
            for oh in data['owner_history']:
                if isinstance(oh, dict):
                    owner_history.append(oh)
                else:
                    owner_history.append({'owner_name': str(oh)})
            data['owner_history'] = owner_history
        
        # Handle transactions
        if 'transactions' in data:
            transactions = []
            for tx in data['transactions']:
                if isinstance(tx, dict):
                    transactions.append(tx)
            data['transactions'] = transactions
        
        return data