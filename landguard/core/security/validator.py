"""
Input validation and security checks.
Prevents injection attacks, path traversal, and malicious input.
"""

import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum


class FileType(Enum):
    """Allowed file types for upload."""
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    IMAGE = "image"  # jpg, png, tiff


class SecurityValidator:
    """Validate and sanitize user inputs to prevent security vulnerabilities."""
    
    # Dangerous patterns that could indicate injection attempts
    DANGEROUS_PATTERNS = [
        r"(\bor\b|\band\b).*[=<>]",  # SQL injection
        r"[;\'\"].*(\bDROP\b|\bDELETE\b|\bUPDATE\b|\bINSERT\b)",  # SQL commands
        r"\$\{.*\}",  # Template injection
        r"<script.*?>",  # XSS
        r"javascript:",  # XSS
        r"\.\./",  # Path traversal
        r"\.\.\\",  # Path traversal (Windows)
        r"(%00|%0a|%0d)",  # Null byte injection
    ]
    
    # Safe characters for different input types
    SAFE_LAND_ID_PATTERN = r"^[A-Z0-9\-_]{1,50}$"
    SAFE_NAME_PATTERN = r"^[a-zA-Z\s\.\-']{1,100}$"
    SAFE_FILENAME_PATTERN = r"^[a-zA-Z0-9\-_.]{1,255}$"
    
    @staticmethod
    def validate_land_id(land_id: str) -> tuple[bool, Optional[str]]:
        """
        Validate land ID format.
        
        Args:
            land_id: Land ID to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not land_id or not isinstance(land_id, str):
            return False, "Land ID must be a non-empty string"
        
        land_id = land_id.strip()
        
        if len(land_id) == 0:
            return False, "Land ID cannot be empty"
        
        if len(land_id) > 50:
            return False, "Land ID too long (max 50 characters)"
        
        # Check for dangerous patterns
        for pattern in SecurityValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, land_id, re.IGNORECASE):
                return False, "Land ID contains invalid characters"
        
        # Check format
        if not re.match(SecurityValidator.SAFE_LAND_ID_PATTERN, land_id):
            return False, "Land ID must contain only alphanumeric characters, hyphens, and underscores"
        
        return True, None
    
    @staticmethod
    def validate_owner_name(name: str) -> tuple[bool, Optional[str]]:
        """
        Validate owner name format.
        
        Args:
            name: Owner name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not isinstance(name, str):
            return False, "Name must be a non-empty string"
        
        name = name.strip()
        
        if len(name) == 0:
            return False, "Name cannot be empty"
        
        if len(name) > 100:
            return False, "Name too long (max 100 characters)"
        
        # Check for dangerous patterns
        for pattern in SecurityValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, name, re.IGNORECASE):
                return False, "Name contains invalid characters"
        
        # Check format (allow letters, spaces, dots, hyphens, apostrophes)
        if not re.match(SecurityValidator.SAFE_NAME_PATTERN, name):
            return False, "Name contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_amount(amount: Any) -> tuple[bool, Optional[str]]:
        """
        Validate transaction amount.
        
        Args:
            amount: Amount to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if amount is None:
            return True, None  # Amount is optional
        
        try:
            amount_float = float(amount)
        except (ValueError, TypeError):
            return False, "Amount must be a number"
        
        if amount_float < 0:
            return False, "Amount cannot be negative"
        
        if amount_float > 1e15:  # 1 quadrillion
            return False, "Amount is unreasonably large"
        
        return True, None
    
    @staticmethod
    def validate_date_string(date_str: str) -> tuple[bool, Optional[str]]:
        """
        Validate date string format.
        
        Args:
            date_str: Date string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not date_str or not isinstance(date_str, str):
            return False, "Date must be a non-empty string"
        
        # Check for dangerous patterns
        for pattern in SecurityValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, date_str, re.IGNORECASE):
                return False, "Date contains invalid characters"
        
        # Check ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        iso_pattern = r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2})?$"
        if not re.match(iso_pattern, date_str):
            return False, "Date must be in ISO format (YYYY-MM-DD)"
        
        return True, None
    
    @staticmethod
    def validate_record_dict(record: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate a complete land record dictionary.
        
        Args:
            record: Record dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate land_id
        if 'land_id' in record:
            valid, error = SecurityValidator.validate_land_id(record['land_id'])
            if not valid:
                errors.append(f"land_id: {error}")
        else:
            errors.append("Missing required field: land_id")
        
        # Validate owner_history
        if 'owner_history' in record and isinstance(record['owner_history'], list):
            for i, owner in enumerate(record['owner_history']):
                if 'owner_name' in owner:
                    valid, error = SecurityValidator.validate_owner_name(owner['owner_name'])
                    if not valid:
                        errors.append(f"owner_history[{i}].owner_name: {error}")
                
                if 'date' in owner:
                    valid, error = SecurityValidator.validate_date_string(str(owner['date']))
                    if not valid:
                        errors.append(f"owner_history[{i}].date: {error}")
        
        # Validate transactions
        if 'transactions' in record and isinstance(record['transactions'], list):
            for i, tx in enumerate(record['transactions']):
                if 'amount' in tx:
                    valid, error = SecurityValidator.validate_amount(tx['amount'])
                    if not valid:
                        errors.append(f"transactions[{i}].amount: {error}")
                
                if 'from_party' in tx:
                    valid, error = SecurityValidator.validate_owner_name(tx['from_party'])
                    if not valid:
                        errors.append(f"transactions[{i}].from_party: {error}")
                
                if 'to_party' in tx:
                    valid, error = SecurityValidator.validate_owner_name(tx['to_party'])
                    if not valid:
                        errors.append(f"transactions[{i}].to_party: {error}")
        
        return len(errors) == 0, errors


class FileValidator:
    """Validate file uploads for security."""
    
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
    
    ALLOWED_EXTENSIONS = {
        FileType.JSON: ['.json'],
        FileType.CSV: ['.csv'],
        FileType.PDF: ['.pdf'],
        FileType.IMAGE: ['.jpg', '.jpeg', '.png', '.tiff', '.tif']
    }
    
    # Magic bytes for file type detection
    MAGIC_BYTES = {
        'pdf': b'%PDF',
        'png': b'\x89PNG',
        'jpg': b'\xff\xd8\xff',
        'tiff_ii': b'II\x2a\x00',  # Little-endian TIFF
        'tiff_mm': b'MM\x00\x2a',  # Big-endian TIFF
    }
    
    @staticmethod
    def validate_filename(filename: str) -> tuple[bool, Optional[str]]:
        """
        Validate filename for security.
        
        Args:
            filename: Filename to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filename or not isinstance(filename, str):
            return False, "Filename must be a non-empty string"
        
        filename = filename.strip()
        
        # Check length
        if len(filename) > 255:
            return False, "Filename too long (max 255 characters)"
        
        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, "Filename contains path traversal characters"
        
        # Check for null bytes
        if '\x00' in filename:
            return False, "Filename contains null bytes"
        
        # Check safe pattern
        if not re.match(SecurityValidator.SAFE_FILENAME_PATTERN, filename):
            return False, "Filename contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_type: FileType) -> tuple[bool, Optional[str]]:
        """
        Validate file extension.
        
        Args:
            filename: Filename to check
            allowed_type: Allowed file type
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        ext = Path(filename).suffix.lower()
        
        if ext not in FileValidator.ALLOWED_EXTENSIONS[allowed_type]:
            allowed = ', '.join(FileValidator.ALLOWED_EXTENSIONS[allowed_type])
            return False, f"File extension not allowed. Allowed: {allowed}"
        
        return True, None
    
    @staticmethod
    def validate_file_size(file_size: int, max_size: Optional[int] = None) -> tuple[bool, Optional[str]]:
        """
        Validate file size.
        
        Args:
            file_size: File size in bytes
            max_size: Maximum allowed size (defaults to MAX_FILE_SIZE)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        max_allowed = max_size or FileValidator.MAX_FILE_SIZE
        
        if file_size <= 0:
            return False, "File is empty"
        
        if file_size > max_allowed:
            max_mb = max_allowed / (1024 * 1024)
            return False, f"File too large (max {max_mb:.1f} MB)"
        
        return True, None
    
    @staticmethod
    def validate_file_content(file_path: Path, expected_type: FileType) -> tuple[bool, Optional[str]]:
        """
        Validate file content by checking magic bytes.
        
        Args:
            file_path: Path to file
            expected_type: Expected file type
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path.exists():
            return False, "File does not exist"
        
        # Read first few bytes
        try:
            with open(file_path, 'rb') as f:
                header = f.read(16)
        except Exception as e:
            return False, f"Cannot read file: {e}"
        
        # Validate based on type
        if expected_type == FileType.PDF:
            if not header.startswith(FileValidator.MAGIC_BYTES['pdf']):
                return False, "File is not a valid PDF"
        
        elif expected_type == FileType.IMAGE:
            is_valid_image = (
                header.startswith(FileValidator.MAGIC_BYTES['png']) or
                header.startswith(FileValidator.MAGIC_BYTES['jpg']) or
                header.startswith(FileValidator.MAGIC_BYTES['tiff_ii']) or
                header.startswith(FileValidator.MAGIC_BYTES['tiff_mm'])
            )
            if not is_valid_image:
                return False, "File is not a valid image"
        
        # JSON and CSV are text files, harder to validate by magic bytes
        # We'll validate them during parsing
        
        return True, None
    
    @staticmethod
    def sanitize_path(file_path: str, base_dir: str) -> tuple[Optional[Path], Optional[str]]:
        """
        Sanitize and validate file path to prevent path traversal.
        
        Args:
            file_path: User-provided file path
            base_dir: Base directory (must be absolute)
            
        Returns:
            Tuple of (safe_path, error_message)
        """
        try:
            base = Path(base_dir).resolve()
            target = (base / file_path).resolve()
            
            # Ensure target is within base directory
            if not str(target).startswith(str(base)):
                return None, "Path traversal detected"
            
            return target, None
        
        except Exception as e:
            return None, f"Invalid path: {e}"