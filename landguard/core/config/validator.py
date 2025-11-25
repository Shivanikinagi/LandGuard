"""
Configuration validator with schema validation.
"""

from typing import Dict, Any, List, Optional


class ConfigValidator:
    """Validate configuration values against schema."""
    
    def __init__(self):
        """Initialize validator with validation rules."""
        self.rules = {
            'rapid_transfer_days': {
                'type': int,
                'min': 1,
                'max': 3650,
                'description': 'Days to check for rapid transfers'
            },
            'rapid_transfer_count': {
                'type': int,
                'min': 2,
                'max': 100,
                'description': 'Minimum transfers to flag as rapid'
            },
            'large_transfer_threshold': {
                'type': (int, float),
                'min': 0,
                'description': 'Threshold for large transfer detection'
            },
            'name_similarity_threshold': {
                'type': (int, float),
                'min': 0,
                'max': 100,
                'description': 'Name matching threshold percentage'
            },
            'date_order_tolerance_days': {
                'type': int,
                'min': 0,
                'max': 365,
                'description': 'Days tolerance for date order conflicts'
            },
            'log_level': {
                'type': str,
                'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                'description': 'Logging level'
            },
            'output_format': {
                'type': str,
                'choices': ['json', 'text', 'csv'],
                'description': 'Output format'
            },
            'enable_verbose': {
                'type': bool,
                'description': 'Enable verbose output'
            }
        }
    
    def validate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration dictionary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Validation result with 'valid' bool and 'errors' list
        """
        errors = []
        
        for key, value in config.items():
            if key not in self.rules:
                continue  # Allow extra keys
            
            rule = self.rules[key]
            error = self._validate_value(key, value, rule)
            
            if error:
                errors.append(error)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'config': config
        }
    
    def _validate_value(self, key: str, value: Any, rule: Dict[str, Any]) -> Optional[str]:
        """
        Validate a single configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
            rule: Validation rule
            
        Returns:
            Error message if validation fails, None otherwise
        """
        # Type check
        expected_type = rule['type']
        if not isinstance(value, expected_type):
            return f"{key}: Expected {expected_type}, got {type(value).__name__}"
        
        # Range check for numeric values
        if isinstance(value, (int, float)):
            if 'min' in rule and value < rule['min']:
                return f"{key}: Value {value} is below minimum {rule['min']}"
            
            if 'max' in rule and value > rule['max']:
                return f"{key}: Value {value} exceeds maximum {rule['max']}"
        
        # Choice check for string values
        if isinstance(value, str) and 'choices' in rule:
            if value not in rule['choices']:
                choices_str = ', '.join(rule['choices'])
                return f"{key}: '{value}' not in allowed choices: {choices_str}"
        
        return None
    
    def get_rule(self, key: str) -> Optional[Dict[str, Any]]:
        """Get validation rule for a configuration key."""
        return self.rules.get(key)
    
    def get_all_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get all validation rules."""
        return self.rules.copy()