"""
Tests for all extractors - fixing import error.
"""

import pytest
import json
import csv
from pathlib import Path

from detector.extractors.base import BaseExtractor
from detector.extractors.json_extractor import JSONExtractor
from detector.extractors.csv_extractor import CSVExtractor
from detector.extractors.pdf_extractor import PDFExtractor
from core.models import LandRecord


class TestExtractorRegistry:
    """Test extractor registration and retrieval."""
    
    def test_json_extractor_exists(self):
        """Test JSON extractor can be instantiated."""
        extractor = JSONExtractor()
        assert isinstance(extractor, BaseExtractor)
    
    def test_csv_extractor_exists(self):
        """Test CSV extractor can be instantiated."""
        extractor = CSVExtractor()
        assert isinstance(extractor, BaseExtractor)
    
    def test_pdf_extractor_exists(self):
        """Test PDF extractor can be instantiated."""
        extractor = PDFExtractor()
        assert isinstance(extractor, BaseExtractor)


class TestBasicExtraction:
    """Basic extraction tests."""
    
    @pytest.fixture
    def sample_json_file(self, tmp_path):
        """Create a sample JSON file."""
        data = {
            "land_id": "TEST-001",
            "owner_history": [{"owner_name": "Test Owner"}],
            "property_area": 1000.0
        }
        file_path = tmp_path / "test.json"
        with open(file_path, 'w') as f:
            json.dump(data, f)
        return file_path
    
    def test_json_extraction(self, sample_json_file):
        """Test basic JSON extraction."""
        extractor = JSONExtractor()
        result = extractor.extract(str(sample_json_file))
        
        assert result['land_id'] == "TEST-001"
        assert len(result['owner_history']) >= 1