"""
CSV file extractor for land records.
"""

import csv
from typing import Dict, Any, List
from pathlib import Path
from collections import defaultdict

from core.models import LandRecord, OwnerHistory, Transaction
from detector.extractors.base import BaseExtractor


class CSVExtractor(BaseExtractor):
    """Extract land records from CSV files."""
    
    def extract(self, file_path: str) -> Dict[str, Any]:
        """
        Extract data from CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dictionary containing extracted land record data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if not rows:
                raise ValueError("Empty CSV file")
            
            # Group rows by land_id
            grouped = self._group_by_land_id(rows)
            
            # Take the first land_id group
            first_land_id = list(grouped.keys())[0]
            return self._normalize_csv(grouped[first_land_id])
            
        except Exception as e:
            raise ValueError(f"Failed to extract CSV: {e}")
    
    def _group_by_land_id(self, rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group CSV rows by land_id."""
        grouped = defaultdict(list)
        for row in rows:
            land_id = row.get('land_id', 'UNKNOWN')
            grouped[land_id].append(row)
        return grouped
    
    def _normalize_csv(self, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Normalize CSV rows to match LandRecord model."""
        
        first_row = rows[0]
        
        # Extract basic fields
        result = {
            'land_id': first_row.get('land_id', 'UNKNOWN'),
            'property_area': self._parse_float(first_row.get('property_area')),
            'registration_number': first_row.get('registration_number'),
            'registration_date': first_row.get('registration_date'),
            'location': first_row.get('location'),
            'property_type': first_row.get('property_type')
        }
        
        # Extract owner history
        owner_history = []
        for row in rows:
            if row.get('owner_name'):
                owner_history.append({
                    'owner_name': row['owner_name'],
                    'date': row.get('owner_date'),
                    'document_id': row.get('owner_doc_id')
                })
        result['owner_history'] = owner_history
        
        # Extract transactions
        transactions = []
        for row in rows:
            if row.get('tx_id'):
                transactions.append({
                    'tx_id': row['tx_id'],
                    'date': row.get('tx_date'),
                    'amount': self._parse_float(row.get('amount')),
                    'from_party': row.get('from_party'),
                    'to_party': row.get('to_party'),
                    'transaction_type': row.get('transaction_type')
                })
        result['transactions'] = transactions
        
        return result
    
    def _parse_float(self, value: Any) -> float | None:
        """Safely parse float value."""
        if not value:
            return None
        try:
            return float(value)
        except:
            return None