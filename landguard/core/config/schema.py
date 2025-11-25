"""
Configuration schema and defaults for LandGuard.
"""

from typing import Dict, Any


class ConfigSchema:
    """Configuration schema with default values."""
    
    @staticmethod
    def get_defaults() -> Dict[str, Any]:
        """
        Get default configuration values.
        
        Returns:
            Dictionary of default configuration values
        """
        return {
            # Fraud Detection Settings
            'rapid_transfer_days': 180,
            'rapid_transfer_count': 2,
            'large_transfer_threshold': 10000000,
            'name_similarity_threshold': 85,
            'date_order_tolerance_days': 1,
            
            # Output Settings
            'log_level': 'INFO',
            'output_format': 'json',
            'enable_verbose': False,
            
            # Feature Flags
            'enable_rapid_transfer_detection': True,
            'enable_large_transfer_detection': True,
            'enable_party_mismatch_detection': True,
            'enable_time_order_detection': True,
            'enable_missing_field_detection': True,
            'enable_duplicate_detection': True,
            
            # Performance Settings
            'batch_size': 100,
            'max_workers': 4,
            'cache_enabled': False,
            
            # File Processing
            'max_file_size_mb': 50,
            'supported_formats': ['json', 'csv', 'pdf', 'jpg', 'png', 'tiff'],
            
            # Report Settings
            'include_evidence': True,
            'include_confidence_scores': True,
            'group_issues_by_severity': True
        }
    
    @staticmethod
    def get_schema() -> Dict[str, Dict[str, Any]]:
        """
        Get configuration schema with types and descriptions.
        
        Returns:
            Dictionary describing configuration schema
        """
        return {
            'rapid_transfer_days': {
                'type': 'integer',
                'default': 180,
                'min': 1,
                'max': 3650,
                'description': 'Number of days to check for rapid ownership transfers'
            },
            'rapid_transfer_count': {
                'type': 'integer',
                'default': 2,
                'min': 2,
                'max': 100,
                'description': 'Minimum number of transfers to flag as rapid'
            },
            'large_transfer_threshold': {
                'type': 'number',
                'default': 10000000,
                'min': 0,
                'description': 'Threshold amount for large transfer detection (in currency units)'
            },
            'name_similarity_threshold': {
                'type': 'number',
                'default': 85,
                'min': 0,
                'max': 100,
                'description': 'Percentage threshold for name similarity matching (0-100)'
            },
            'date_order_tolerance_days': {
                'type': 'integer',
                'default': 1,
                'min': 0,
                'max': 365,
                'description': 'Days tolerance for date order conflicts'
            },
            'log_level': {
                'type': 'string',
                'default': 'INFO',
                'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                'description': 'Logging level'
            },
            'output_format': {
                'type': 'string',
                'default': 'json',
                'choices': ['json', 'text', 'csv'],
                'description': 'Default output format for reports'
            },
            'enable_verbose': {
                'type': 'boolean',
                'default': False,
                'description': 'Enable verbose output with detailed evidence'
            },
            'batch_size': {
                'type': 'integer',
                'default': 100,
                'min': 1,
                'max': 10000,
                'description': 'Number of records to process in each batch'
            },
            'max_workers': {
                'type': 'integer',
                'default': 4,
                'min': 1,
                'max': 32,
                'description': 'Maximum number of worker threads for parallel processing'
            }
        }
    
    @staticmethod
    def generate_yaml_template() -> str:
        """
        Generate YAML configuration template with comments.
        
        Returns:
            YAML configuration template as string
        """
        schema = ConfigSchema.get_schema()
        defaults = ConfigSchema.get_defaults()
        
        lines = [
            "# LandGuard Configuration",
            "# Generated configuration template",
            "",
            "# ============================================",
            "# Fraud Detection Settings",
            "# ============================================",
            ""
        ]
        
        fraud_keys = [
            'rapid_transfer_days',
            'rapid_transfer_count',
            'large_transfer_threshold',
            'name_similarity_threshold',
            'date_order_tolerance_days'
        ]
        
        for key in fraud_keys:
            if key in schema:
                s = schema[key]
                lines.append(f"# {s['description']}")
                if 'min' in s and 'max' in s:
                    lines.append(f"# Range: {s['min']} - {s['max']}")
                lines.append(f"{key}: {defaults[key]}")
                lines.append("")
        
        lines.extend([
            "# ============================================",
            "# Output Settings",
            "# ============================================",
            ""
        ])
        
        output_keys = ['log_level', 'output_format', 'enable_verbose']
        
        for key in output_keys:
            if key in schema:
                s = schema[key]
                lines.append(f"# {s['description']}")
                if 'choices' in s:
                    choices = ', '.join(s['choices'])
                    lines.append(f"# Choices: {choices}")
                lines.append(f"{key}: {defaults[key]}")
                lines.append("")
        
        return '\n'.join(lines)