"""
Large dataset generator for performance testing.
Creates realistic test data at scale.
"""

import json
import csv
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict


class LargeDatasetGenerator:
    """Generate large datasets for performance testing."""
    
    def __init__(self, seed: int = 42):
        """Initialize generator with random seed for reproducibility."""
        random.seed(seed)
        self.first_names = [
            "John", "Jane", "Michael", "Sarah", "David", "Emily", 
            "Robert", "Lisa", "James", "Mary", "William", "Patricia",
            "Richard", "Jennifer", "Thomas", "Linda", "Charles", "Barbara"
        ]
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
            "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez"
        ]
    
    def generate_owner_name(self) -> str:
        """Generate random owner name."""
        first = random.choice(self.first_names)
        last = random.choice(self.last_names)
        return f"{first} {last}"
    
    def generate_land_id(self, index: int) -> str:
        """Generate land ID."""
        return f"LD-{index:06d}"
    
    def generate_owner_history(self, count: int, start_date: datetime) -> List[Dict]:
        """Generate owner history with specified count."""
        owners = []
        current_date = start_date
        
        for i in range(count):
            owner = {
                "owner_name": self.generate_owner_name(),
                "date": current_date.isoformat(),
                "document_id": f"DOC-{i:06d}"
            }
            owners.append(owner)
            
            # Next transfer 30-365 days later
            days_later = random.randint(30, 365)
            current_date = current_date + timedelta(days=days_later)
        
        return owners
    
    def generate_transactions(self, count: int, owners: List[Dict]) -> List[Dict]:
        """Generate transactions based on owner history."""
        transactions = []
        
        for i in range(count):
            # Pick random owners for from/to parties
            from_idx = random.randint(0, len(owners) - 2)
            to_idx = from_idx + 1
            
            transaction = {
                "tx_id": f"TX-{i:06d}",
                "date": owners[to_idx]["date"],
                "amount": random.randint(500000, 50000000),
                "from_party": owners[from_idx]["owner_name"],
                "to_party": owners[to_idx]["owner_name"],
                "transaction_type": random.choice(["sale", "transfer", "inheritance"])
            }
            transactions.append(transaction)
        
        return transactions
    
    def generate_json_record(self, index: int, 
                            owner_count: int = 10, 
                            transaction_count: int = 5) -> Dict:
        """Generate a single land record as dictionary."""
        start_date = datetime(2010, 1, 1) + timedelta(days=random.randint(0, 3650))
        owners = self.generate_owner_history(owner_count, start_date)
        transactions = self.generate_transactions(
            min(transaction_count, owner_count - 1), 
            owners
        )
        
        return {
            "land_id": self.generate_land_id(index),
            "owner_history": owners,
            "transactions": transactions,
            "property_area": round(random.uniform(500, 10000), 2),
            "registration_number": f"REG-{index:06d}",
            "location": f"{random.randint(1, 999)} Main Street"
        }
    
    def generate_json_files(self, output_dir: Path, 
                           count: int = 100,
                           owner_count: int = 10,
                           transaction_count: int = 5) -> List[Path]:
        """
        Generate multiple JSON files.
        
        Args:
            output_dir: Directory to save files
            count: Number of files to generate
            owner_count: Number of owners per record
            transaction_count: Number of transactions per record
        
        Returns:
            List of generated file paths
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        file_paths = []
        
        for i in range(count):
            record = self.generate_json_record(i, owner_count, transaction_count)
            
            file_path = output_dir / f"record_{i:06d}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(record, f, indent=2)
            
            file_paths.append(file_path)
        
        return file_paths
    
    def generate_csv_file(self, output_path: Path,
                         record_count: int = 100,
                         owners_per_record: int = 10) -> Path:
        """
        Generate a large CSV file with multiple records.
        
        Args:
            output_path: Path to save CSV file
            record_count: Number of land records
            owners_per_record: Number of owners per record
        
        Returns:
            Path to generated file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        fieldnames = [
            'land_id', 'owner_name', 'owner_date', 'document_id',
            'tx_id', 'amount', 'from_party', 'to_party',
            'property_area', 'registration_number', 'location'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for i in range(record_count):
                record = self.generate_json_record(i, owners_per_record, owners_per_record - 1)
                land_id = record['land_id']
                
                # Write each owner as a row
                for j, owner in enumerate(record['owner_history']):
                    row = {
                        'land_id': land_id,
                        'owner_name': owner['owner_name'],
                        'owner_date': owner['date'],
                        'document_id': owner.get('document_id', ''),
                        'tx_id': '',
                        'amount': '',
                        'from_party': '',
                        'to_party': '',
                        'property_area': record['property_area'],
                        'registration_number': record['registration_number'],
                        'location': record['location']
                    }
                    
                    # Add transaction data if available
                    if j < len(record['transactions']):
                        tx = record['transactions'][j]
                        row.update({
                            'tx_id': tx['tx_id'],
                            'amount': tx['amount'],
                            'from_party': tx['from_party'],
                            'to_party': tx['to_party']
                        })
                    
                    writer.writerow(row)
        
        return output_path
    
    def generate_mixed_quality_data(self, output_dir: Path, count: int = 50):
        """
        Generate dataset with intentional quality issues for testing.
        
        Includes:
        - Missing fields
        - Rapid transfers
        - Party mismatches
        - Large transfers
        - Duplicate IDs
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i in range(count):
            record = self.generate_json_record(i)
            
            # Inject issues in 30% of records
            if random.random() < 0.3:
                issue_type = random.choice([
                    'missing_field', 'rapid_transfer', 
                    'party_mismatch', 'large_transfer'
                ])
                
                if issue_type == 'missing_field':
                    # Remove random field
                    if random.random() < 0.5:
                        record.pop('registration_number', None)
                    else:
                        record.pop('property_area', None)
                
                elif issue_type == 'rapid_transfer':
                    # Create rapid transfers (3 in 60 days)
                    start_date = datetime(2024, 1, 1)
                    record['owner_history'] = [
                        {
                            "owner_name": self.generate_owner_name(),
                            "date": (start_date + timedelta(days=j*20)).isoformat()
                        }
                        for j in range(3)
                    ]
                
                elif issue_type == 'party_mismatch':
                    # Create transaction with wrong party
                    if record.get('transactions'):
                        record['transactions'][0]['from_party'] = self.generate_owner_name()
                
                elif issue_type == 'large_transfer':
                    # Create very large transaction
                    if record.get('transactions'):
                        record['transactions'][0]['amount'] = 100000000  # 100M
            
            file_path = output_dir / f"mixed_quality_{i:03d}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(record, f, indent=2)


# Convenience functions for tests
def generate_test_files(output_dir: Path, count: int = 10) -> List[Path]:
    """Generate test files quickly."""
    generator = LargeDatasetGenerator()
    return generator.generate_json_files(output_dir, count, owner_count=5, transaction_count=3)


def generate_large_test_files(output_dir: Path, count: int = 100) -> List[Path]:
    """Generate large test dataset."""
    generator = LargeDatasetGenerator()
    return generator.generate_json_files(output_dir, count, owner_count=50, transaction_count=25)