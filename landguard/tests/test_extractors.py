"""
Comprehensive tests for all file extractors.
Tests edge cases, error handling, and data validation.
"""

import pytest
import json
import csv
from pathlib import Path
from datetime import datetime

from detector.extractors.json_extractor import JSONExtractor
from detector.extractors.csv_extractor import CSVExtractor
from detector.extractors.pdf_extractor import PDFExtractor
from core.models import LandRecord


class TestJSONExtractor:
    """Test suite for JSON extractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create JSON extractor instance."""
        return JSONExtractor()
    
    @pytest.fixture
    def sample_json_data(self):
        """Sample valid JSON data."""
        return {
            "land_id": "LD-TEST-001",
            "owner_history": [
                {
                    "owner_name": "John Doe",
                    "date": "2020-01-01",
                    "document_id": "DOC-001"
                },
                {
                    "owner_name": "Jane Smith",
                    "date": "2023-06-15",
                    "document_id": "DOC-002"
                }
            ],
            "transactions": [
                {
                    "tx_id": "TX-001",
                    "date": "2023-06-15",
                    "amount": 5000000,
                    "from_party": "John Doe",
                    "to_party": "Jane Smith",
                    "transaction_type": "sale"
                }
            ],
            "property_area": 2500.5,
            "registration_number": "REG-2020-001",
            "location": "123 Main St"
        }
    
    def test_extract_single_record(self, extractor, sample_json_data, tmp_path):
        """Test extracting a single valid JSON record."""
        test_file = tmp_path / "test_record.json"
        with open(test_file, 'w') as f:
            json.dump(sample_json_data, f)
        
        result = extractor.extract(str(test_file))
        
        assert result['land_id'] == "LD-TEST-001"
        assert len(result['owner_history']) == 2
        assert len(result['transactions']) == 1
        assert result['property_area'] == 2500.5
    
    def test_extract_array_format(self, extractor, sample_json_data, tmp_path):
        """Test extracting from JSON array format."""
        test_file = tmp_path / "test_array.json"
        with open(test_file, 'w') as f:
            json.dump([sample_json_data], f)
        
        result = extractor.extract(str(test_file))
        
        assert result['land_id'] == "LD-TEST-001"
        assert isinstance(result['owner_history'], list)
    
    def test_empty_json_array(self, extractor, tmp_path):
        """Test handling of empty JSON array."""
        test_file = tmp_path / "empty_array.json"
        with open(test_file, 'w') as f:
            json.dump([], f)
        
        with pytest.raises(ValueError, match="Empty JSON array"):
            extractor.extract(str(test_file))
    
    def test_invalid_json_format(self, extractor, tmp_path):
        """Test handling of invalid JSON syntax."""
        test_file = tmp_path / "invalid.json"
        with open(test_file, 'w') as f:
            f.write("{invalid json")
        
        with pytest.raises(ValueError, match="Invalid JSON format"):
            extractor.extract(str(test_file))
    
    def test_normalize_simple_owner_history(self, extractor):
        """Test normalization of simple owner name strings."""
        data = {
            "land_id": "LD-002",
            "owner_history": ["Alice", "Bob", "Charlie"]
        }
        
        normalized = extractor._normalize_json(data)
        
        assert len(normalized['owner_history']) == 3
        assert all(isinstance(oh, dict) for oh in normalized['owner_history'])
        assert normalized['owner_history'][0]['owner_name'] == "Alice"
    
    def test_missing_optional_fields(self, extractor, tmp_path):
        """Test handling records with missing optional fields."""
        minimal_data = {
            "land_id": "LD-MINIMAL",
            "owner_history": [{"owner_name": "Test Owner"}]
        }
        
        test_file = tmp_path / "minimal.json"
        with open(test_file, 'w') as f:
            json.dump(minimal_data, f)
        
        result = extractor.extract(str(test_file))
        
        assert result['land_id'] == "LD-MINIMAL"
        assert 'owner_history' in result


class TestCSVExtractor:
    """Test suite for CSV extractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create CSV extractor instance."""
        return CSVExtractor()
    
    def test_extract_single_land_record(self, extractor, tmp_path):
        """Test extracting a single land record from CSV."""
        test_file = tmp_path / "test.csv"
        
        with open(test_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'land_id', 'owner_name', 'owner_date', 
                'property_area', 'registration_number'
            ])
            writer.writeheader()
            writer.writerow({
                'land_id': 'LD-CSV-001',
                'owner_name': 'Alice Johnson',
                'owner_date': '2022-01-15',
                'property_area': '1500.5',
                'registration_number': 'REG-CSV-001'
            })
        
        result = extractor.extract(str(test_file))
        
        assert result['land_id'] == 'LD-CSV-001'
        assert len(result['owner_history']) >= 1
        assert result['owner_history'][0]['owner_name'] == 'Alice Johnson'
        assert result['property_area'] == 1500.5
    
    def test_extract_multiple_owners_same_land(self, extractor, tmp_path):
        """Test extracting multiple ownership records for same land."""
        test_file = tmp_path / "multi_owner.csv"
        
        with open(test_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'land_id', 'owner_name', 'owner_date'
            ])
            writer.writeheader()
            writer.writerow({
                'land_id': 'LD-CSV-002',
                'owner_name': 'Owner 1',
                'owner_date': '2020-01-01'
            })
            writer.writerow({
                'land_id': 'LD-CSV-002',
                'owner_name': 'Owner 2',
                'owner_date': '2021-01-01'
            })
            writer.writerow({
                'land_id': 'LD-CSV-002',
                'owner_name': 'Owner 3',
                'owner_date': '2022-01-01'
            })
        
        result = extractor.extract(str(test_file))
        
        assert result['land_id'] == 'LD-CSV-002'
        assert len(result['owner_history']) == 3
    
    def test_extract_with_transactions(self, extractor, tmp_path):
        """Test extracting transactions from CSV."""
        test_file = tmp_path / "with_tx.csv"
        
        with open(test_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'land_id', 'owner_name', 'tx_id', 'amount', 
                'from_party', 'to_party'
            ])
            writer.writeheader()
            writer.writerow({
                'land_id': 'LD-CSV-003',
                'owner_name': 'Alice',
                'tx_id': 'TX-CSV-001',
                'amount': '2500000',
                'from_party': 'Alice',
                'to_party': 'Bob'
            })
        
        result = extractor.extract(str(test_file))
        
        assert len(result['transactions']) >= 1
        assert result['transactions'][0]['tx_id'] == 'TX-CSV-001'
        assert result['transactions'][0]['amount'] == 2500000
    
    def test_empty_csv_file(self, extractor, tmp_path):
        """Test handling of empty CSV file."""
        test_file = tmp_path / "empty.csv"
        with open(test_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['land_id', 'owner_name'])
        
        with pytest.raises(ValueError, match="Empty CSV file"):
            extractor.extract(str(test_file))
    
    def test_parse_invalid_float(self, extractor):
        """Test parsing invalid float values."""
        assert extractor._parse_float(None) is None
        assert extractor._parse_float("") is None
        assert extractor._parse_float("invalid") is None
        assert extractor._parse_float("123.45") == 123.45
        assert extractor._parse_float(456.78) == 456.78


class TestPDFExtractor:
    """Test suite for PDF extractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create PDF extractor instance."""
        return PDFExtractor()
    
    def test_extract_land_id_from_text(self, extractor):
        """Test extracting land ID from text."""
        text = "Land ID: LD-PDF-001\nOwner: Test Owner"
        land_id = extractor._extract_land_id(text)
        assert land_id == "LD-PDF-001"
    
    def test_extract_land_id_alternative_formats(self, extractor):
        """Test extracting land ID with alternative keywords."""
        text1 = "Property ID: PROP-123\n"
        assert extractor._extract_land_id(text1) == "PROP-123"
        
        text2 = "Parcel: PARC-456\n"
        assert extractor._extract_land_id(text2) == "PARC-456"
    
    def test_extract_land_id_not_found(self, extractor):
        """Test handling when land ID is not found."""
        text = "Some document without land ID"
        assert extractor._extract_land_id(text) == "UNKNOWN"
    
    def test_extract_owners_from_text(self, extractor):
        """Test extracting owner names from text."""
        text = "Owner: John Smith\nDate: 2023-01-01\nOwner: Jane Doe"
        owners = extractor._extract_owners(text)
        
        assert len(owners) >= 1
        assert any("John Smith" in o['owner_name'] for o in owners)
    
    def test_extract_property_area(self, extractor):
        """Test extracting property area from text."""
        text1 = "Area: 2,500.50 sqm"
        assert extractor._extract_property_area(text1) == 2500.50
        
        text2 = "Size: 1500 sq"
        assert extractor._extract_property_area(text2) == 1500.0
    
    def test_extract_registration_number(self, extractor):
        """Test extracting registration number."""
        text = "Registration: REG-2023-001"
        reg_num = extractor._extract_registration_number(text)
        assert reg_num == "REG-2023-001"
    
    def test_parse_text_complete(self, extractor):
        """Test complete text parsing."""
        text = """
        Land ID: LD-FULL-001
        Owner: Alice Smith
        Registration: REG-001
        Area: 3000 sqm
        Transaction: TX-001
        """
        
        result = extractor._parse_text(text)
        
        assert result['land_id'] == "LD-FULL-001"
        assert result['registration_number'] == "REG-001"
        assert result['property_area'] == 3000.0
        assert len(result['owner_history']) > 0
        assert result['extraction_confidence'] == 0.7


class TestIntegration:
    """Integration tests for full analysis pipeline."""
    
    def test_json_to_landrecord_conversion(self, tmp_path):
        """Test complete pipeline from JSON file to LandRecord."""
        data = {
            "land_id": "LD-INT-001",
            "owner_history": [
                {"owner_name": "Alice", "date": "2020-01-01"},
                {"owner_name": "Bob", "date": "2020-02-01"}
            ],
            "property_area": 1000.0
        }
        
        test_file = tmp_path / "integration.json"
        with open(test_file, 'w') as f:
            json.dump(data, f)
        
        extractor = JSONExtractor()
        extracted = extractor.extract(str(test_file))
        
        record = LandRecord(**extracted)
        
        assert record.land_id == "LD-INT-001"
        assert len(record.owner_history) == 2
        assert record.property_area == 1000.0
    
    def test_csv_to_landrecord_conversion(self, tmp_path):
        """Test complete pipeline from CSV to LandRecord."""
        test_file = tmp_path / "integration.csv"
        
        with open(test_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'land_id', 'owner_name', 'property_area'
            ])
            writer.writeheader()
            writer.writerow({
                'land_id': 'LD-INT-002',
                'owner_name': 'Test Owner',
                'property_area': '2000.5'
            })
        
        extractor = CSVExtractor()
        extracted = extractor.extract(str(test_file))
        
        record = LandRecord(**extracted)
        
        assert record.land_id == 'LD-INT-002'
        assert record.property_area == 2000.5


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_very_large_owner_history(self, tmp_path):
        """Test handling of very large owner history."""
        large_history = [
            {"owner_name": f"Owner {i}", "date": f"2020-{i%12+1:02d}-01"}
            for i in range(1000)
        ]
        
        data = {
            "land_id": "LD-LARGE",
            "owner_history": large_history
        }
        
        test_file = tmp_path / "large.json"
        with open(test_file, 'w') as f:
            json.dump(data, f)
        
        extractor = JSONExtractor()
        result = extractor.extract(str(test_file))
        
        assert len(result['owner_history']) == 1000
    
    def test_unicode_characters_in_names(self, tmp_path):
        """Test handling of unicode characters."""
        data = {
            "land_id": "LD-UNICODE",
            "owner_history": [
                {"owner_name": "José García", "date": "2020-01-01"},
                {"owner_name": "李明", "date": "2021-01-01"},
                {"owner_name": "Müller", "date": "2022-01-01"}
            ]
        }
        
        test_file = tmp_path / "unicode.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        
        extractor = JSONExtractor()
        result = extractor.extract(str(test_file))
        
        assert result['owner_history'][0]['owner_name'] == "José García"
        assert result['owner_history'][1]['owner_name'] == "李明"
    
    def test_special_characters_in_land_id(self, tmp_path):
        """Test handling of special characters in land IDs."""
        data = {
            "land_id": "LD-2023/TEST#001",
            "owner_history": [{"owner_name": "Test"}]
        }
        
        test_file = tmp_path / "special.json"
        with open(test_file, 'w') as f:
            json.dump(data, f)
        
        extractor = JSONExtractor()
        result = extractor.extract(str(test_file))
        
        assert result['land_id'] == "LD-2023/TEST#001"