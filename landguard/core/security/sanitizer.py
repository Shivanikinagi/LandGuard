"""
Data sanitization utilities.
Clean and escape user input to prevent XSS, injection attacks, and data corruption.
"""

import re
import html
from typing import Any, Dict, List, Optional, Union
from pathlib import Path


class DataSanitizer:
    """Sanitize user input data for security."""
    
    # Characters to remove or escape
    CONTROL_CHARS = r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]'
    
    # HTML entities that should be escaped
    HTML_ESCAPE_TABLE = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#x27;",
        ">": "&gt;",
        "<": "&lt;",
    }
    
    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize a string value.
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return str(value)
        
        # Remove control characters
        sanitized = re.sub(DataSanitizer.CONTROL_CHARS, '', value)
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        # Trim to max length if specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_html(value: str) -> str:
        """
        Escape HTML entities to prevent XSS.
        
        Args:
            value: String that may contain HTML
            
        Returns:
            HTML-escaped string
        """
        if not isinstance(value, str):
            return str(value)
        
        return html.escape(value, quote=True)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other attacks.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Safe filename
        """
        if not isinstance(filename, str):
            filename = str(filename)
        
        # Remove path components
        filename = Path(filename).name
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\s\-.]', '', filename)
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Replace multiple dots with single dot
        filename = re.sub(r'\.{2,}', '.', filename)
        
        # Ensure not empty
        if not filename:
            filename = 'unnamed'
        
        # Limit length
        if len(filename) > 255:
            name_part = filename[:240]
            ext_part = Path(filename).suffix[:15]
            filename = name_part + ext_part
        
        return filename
    
    @staticmethod
    def sanitize_land_id(land_id: str) -> str:
        """
        Sanitize land ID.
        
        Args:
            land_id: Land ID to sanitize
            
        Returns:
            Sanitized land ID
        """
        if not isinstance(land_id, str):
            land_id = str(land_id)
        
        # Keep only alphanumeric, hyphens, and underscores
        sanitized = re.sub(r'[^A-Z0-9\-_]', '', land_id.upper())
        
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        
        return sanitized
    
    @staticmethod
    def sanitize_owner_name(name: str) -> str:
        """
        Sanitize owner name.
        
        Args:
            name: Owner name to sanitize
            
        Returns:
            Sanitized name
        """
        if not isinstance(name, str):
            name = str(name)
        
        # Remove control characters
        sanitized = re.sub(DataSanitizer.CONTROL_CHARS, '', name)
        
        # Keep only letters, spaces, dots, hyphens, apostrophes
        sanitized = re.sub(r"[^a-zA-Z\s.\-']", '', sanitized)
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_amount(amount: Any) -> Optional[float]:
        """
        Sanitize transaction amount.
        
        Args:
            amount: Amount to sanitize
            
        Returns:
            Sanitized amount as float or None
        """
        if amount is None:
            return None
        
        try:
            # Convert to float
            amount_float = float(amount)
            
            # Ensure non-negative
            if amount_float < 0:
                return 0.0
            
            # Cap at reasonable maximum
            if amount_float > 1e15:
                return 1e15
            
            # Round to 2 decimal places
            return round(amount_float, 2)
        
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any], fields_config: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Recursively sanitize a dictionary.
        
        Args:
            data: Dictionary to sanitize
            fields_config: Optional field-specific sanitization config
                          Format: {'field_name': 'sanitizer_type'}
                          Types: 'string', 'html', 'filename', 'land_id', 'name', 'amount'
            
        Returns:
            Sanitized dictionary
        """
        if not isinstance(data, dict):
            return {}
        
        fields_config = fields_config or {}
        sanitized = {}
        
        for key, value in data.items():
            # Sanitize key
            safe_key = DataSanitizer.sanitize_string(str(key), max_length=100)
            
            # Sanitize value based on type and config
            if isinstance(value, dict):
                sanitized[safe_key] = DataSanitizer.sanitize_dict(value, fields_config)
            
            elif isinstance(value, list):
                sanitized[safe_key] = [
                    DataSanitizer.sanitize_dict(item, fields_config) if isinstance(item, dict)
                    else DataSanitizer._sanitize_value(item, fields_config.get(key, 'string'))
                    for item in value
                ]
            
            else:
                sanitizer_type = fields_config.get(key, 'string')
                sanitized[safe_key] = DataSanitizer._sanitize_value(value, sanitizer_type)
        
        return sanitized
    
    @staticmethod
    def _sanitize_value(value: Any, sanitizer_type: str) -> Any:
        """
        Sanitize a single value based on type.
        
        Args:
            value: Value to sanitize
            sanitizer_type: Type of sanitization to apply
            
        Returns:
            Sanitized value
        """
        if value is None:
            return None
        
        if sanitizer_type == 'html':
            return DataSanitizer.sanitize_html(str(value))
        
        elif sanitizer_type == 'filename':
            return DataSanitizer.sanitize_filename(str(value))
        
        elif sanitizer_type == 'land_id':
            return DataSanitizer.sanitize_land_id(str(value))
        
        elif sanitizer_type == 'name':
            return DataSanitizer.sanitize_owner_name(str(value))
        
        elif sanitizer_type == 'amount':
            return DataSanitizer.sanitize_amount(value)
        
        elif sanitizer_type == 'string':
            if isinstance(value, str):
                return DataSanitizer.sanitize_string(value)
            return value
        
        else:
            return value
    
    @staticmethod
    def sanitize_land_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize a land record with field-specific rules.
        
        Args:
            record: Land record dictionary
            
        Returns:
            Sanitized land record
        """
        fields_config = {
            'land_id': 'land_id',
            'owner_name': 'name',
            'from_party': 'name',
            'to_party': 'name',
            'amount': 'amount',
            'source_file': 'filename',
            'registration_number': 'string',
            'description': 'html',
            'notes': 'html',
        }
        
        return DataSanitizer.sanitize_dict(record, fields_config)
    
    @staticmethod
    def remove_sensitive_data(data: Dict[str, Any], sensitive_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Remove or redact sensitive data from dictionary.
        
        Args:
            data: Dictionary that may contain sensitive data
            sensitive_fields: List of field names to redact (default: common sensitive fields)
            
        Returns:
            Dictionary with sensitive data removed
        """
        if sensitive_fields is None:
            sensitive_fields = [
                'password', 'secret', 'token', 'api_key', 'private_key',
                'ssn', 'credit_card', 'cvv', 'pin'
            ]
        
        cleaned = {}
        
        for key, value in data.items():
            # Check if key contains sensitive field name
            is_sensitive = any(
                sensitive_field.lower() in key.lower()
                for sensitive_field in sensitive_fields
            )
            
            if is_sensitive:
                cleaned[key] = '[REDACTED]'
            
            elif isinstance(value, dict):
                cleaned[key] = DataSanitizer.remove_sensitive_data(value, sensitive_fields)
            
            elif isinstance(value, list):
                cleaned[key] = [
                    DataSanitizer.remove_sensitive_data(item, sensitive_fields)
                    if isinstance(item, dict) else item
                    for item in value
                ]
            
            else:
                cleaned[key] = value
        
        return cleaned
    
    @staticmethod
    def sanitize_for_logging(data: Any) -> str:
        """
        Sanitize data for safe logging (remove sensitive info, limit size).
        
        Args:
            data: Data to sanitize for logging
            
        Returns:
            Safe string representation
        """
        if isinstance(data, dict):
            # Remove sensitive fields
            cleaned = DataSanitizer.remove_sensitive_data(data)
            
            # Convert to string
            result = str(cleaned)
        
        else:
            result = str(data)
        
        # Limit length
        max_length = 1000
        if len(result) > max_length:
            result = result[:max_length] + '... [truncated]'
        
        # Remove control characters
        result = re.sub(DataSanitizer.CONTROL_CHARS, '', result)
        
        return result