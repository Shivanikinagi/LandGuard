"""
Tests for security validator.
"""

import pytest
import tempfile
from pathlib import Path
from core.security.validator import (
    SecurityValidator,
    FileValidator,
    FileType
)


class TestSecurityValidator:
    """Test security validation functions."""
    
    def test_validate_land_id_valid(self):
        """Test valid land ID."""
        valid, error = SecurityValidator.validate_land_id("LAND-123-ABC")
        assert valid is True
        assert error is None
    
    def test_validate_land_id_invalid_characters(self):
        """Test land ID with invalid characters."""
        valid, error = SecurityValidator.validate_land_id("LAND<script>")
        assert valid is False
        assert "invalid characters" in error.lower()
    
    def test_validate_land_id_sql_injection(self):
        """Test land ID with SQL injection attempt."""
        valid, error = SecurityValidator.validate_land_id("' OR '1'='1")
        assert valid is False
        assert error is not None
    
    def test_validate_land_id_too_long(self):
        """Test land ID that's too long."""
        valid, error = SecurityValidator.validate_land_id("A" * 51)
        assert valid is False
        assert "too long" in error.lower()
    
    def test_validate_land_id_empty(self):
        """Test empty land ID."""
        valid, error = SecurityValidator.validate_land_id("")
        assert valid is False
        assert "empty" in error.lower()
    
    def test_validate_owner_name_valid(self):
        """Test valid owner name."""
        valid, error = SecurityValidator.validate_owner_name("John O'Brien-Smith")
        assert valid is True
        assert error is None
    
    def test_validate_owner_name_xss_attempt(self):
        """Test owner name with XSS attempt."""
        valid, error = SecurityValidator.validate_owner_name("<script>alert('XSS')</script>")
        assert valid is False
        assert error is not None
    
    def test_validate_owner_name_too_long(self):
        """Test owner name that's too long."""
        valid, error = SecurityValidator.validate_owner_name("A" * 101)
        assert valid is False
        assert "too long" in error.lower()
    
    def test_validate_amount_valid(self):
        """Test valid amount."""
        valid, error = SecurityValidator.validate_amount(1000.50)
        assert valid is True
        assert error is None
    
    def test_validate_amount_negative(self):
        """Test negative amount."""
        valid, error = SecurityValidator.validate_amount(-100)
        assert valid is False
        assert "negative" in error.lower()
    
    def test_validate_amount_too_large(self):
        """Test unreasonably large amount."""
        valid, error = SecurityValidator.validate_amount(1e16)
        assert valid is False
        assert "large" in error.lower()
    
    def test_validate_amount_none(self):
        """Test None amount (should be allowed)."""
        valid, error = SecurityValidator.validate_amount(None)
        assert valid is True
        assert error is None
    
    def test_validate_date_string_valid(self):
        """Test valid date string."""
        valid, error = SecurityValidator.validate_date_string("2024-01-15")
        assert valid is True
        assert error is None
    
    def test_validate_date_string_with_time(self):
        """Test valid date string with time."""
        valid, error = SecurityValidator.validate_date_string("2024-01-15T10:30:00")
        assert valid is True
        assert error is None
    
    def test_validate_date_string_invalid_format(self):
        """Test invalid date format."""
        valid, error = SecurityValidator.validate_date_string("15/01/2024")
        assert valid is False
        assert "ISO format" in error
    
    def test_validate_record_dict_valid(self):
        """Test validation of valid record."""
        record = {
            'land_id': 'LAND-123',
            'owner_history': [
                {
                    'owner_name': 'John Doe',
                    'date': '2024-01-01'
                }
            ],
            'transactions': [
                {
                    'amount': 100000,
                    'from_party': 'John Doe',
                    'to_party': 'Jane Smith'
                }
            ]
        }
        
        valid, errors = SecurityValidator.validate_record_dict(record)
        assert valid is True
        assert len(errors) == 0
    
    def test_validate_record_dict_missing_land_id(self):
        """Test record without land_id."""
        record = {
            'owner_history': []
        }
        
        valid, errors = SecurityValidator.validate_record_dict(record)
        assert valid is False
        assert any('land_id' in err for err in errors)


class TestFileValidator:
    """Test file validation functions."""
    
    def test_validate_filename_valid(self):
        """Test valid filename."""
        valid, error = FileValidator.validate_filename("document.pdf")
        assert valid is True
        assert error is None
    
    def test_validate_filename_path_traversal(self):
        """Test filename with path traversal."""
        valid, error = FileValidator.validate_filename("../../../etc/passwd")
        assert valid is False
        assert "path traversal" in error.lower()
    
    def test_validate_filename_null_byte(self):
        """Test filename with null byte."""
        valid, error = FileValidator.validate_filename("file\x00.txt")
        assert valid is False
        assert "null byte" in error.lower()
    
    def test_validate_file_extension_json_valid(self):
        """Test valid JSON file extension."""
        valid, error = FileValidator.validate_file_extension(
            "data.json",
            FileType.JSON
        )
        assert valid is True
        assert error is None
    
    def test_validate_file_extension_invalid(self):
        """Test invalid file extension."""
        valid, error = FileValidator.validate_file_extension(
            "data.exe",
            FileType.JSON
        )
        assert valid is False
        assert "not allowed" in error.lower()
    
    def test_validate_file_size_valid(self):
        """Test valid file size."""
        valid, error = FileValidator.validate_file_size(1024 * 1024)  # 1 MB
        assert valid is True
        assert error is None
    
    def test_validate_file_size_too_large(self):
        """Test file that's too large."""
        valid, error = FileValidator.validate_file_size(200 * 1024 * 1024)  # 200 MB
        assert valid is False
        assert "too large" in error.lower()
    
    def test_validate_file_size_empty(self):
        """Test empty file."""
        valid, error = FileValidator.validate_file_size(0)
        assert valid is False
        assert "empty" in error.lower()
    
    def test_sanitize_path_valid(self):
        """Test path sanitization with valid path."""
        # Use temporary directory to be cross-platform
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = str(Path(tmpdir).resolve())
            safe_path, error = FileValidator.sanitize_path("file.txt", base_dir)
            
            assert error is None
            assert safe_path is not None
            # Convert both to resolved paths for comparison
            assert str(safe_path.resolve()).startswith(str(Path(base_dir).resolve()))
    
    def test_sanitize_path_traversal_attempt(self):
        """Test path sanitization with traversal attempt."""
        # Use temporary directory to be cross-platform
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = str(Path(tmpdir).resolve())
            safe_path, error = FileValidator.sanitize_path("../../etc/passwd", base_dir)
            
            assert error is not None
            assert "path traversal" in error.lower()
            assert safe_path is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])