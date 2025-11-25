"""
Configuration loader with YAML and environment variable support.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .validator import ConfigValidator
from .schema import ConfigSchema


class ConfigLoader:
    """Load and manage configuration from YAML files and environment variables."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to YAML config file (optional)
        """
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self._validator = ConfigValidator()
        self._load_defaults()
        
        if config_path:
            self._load_yaml(config_path)
        
        self._load_env_variables()
        self._validate()
    
    def _load_defaults(self):
        """Load default configuration values."""
        default_config_path = Path(__file__).parent.parent.parent / "config" / "default.yaml"
        
        if default_config_path.exists():
            with open(default_config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            # Hardcoded defaults if file doesn't exist
            self._config = ConfigSchema.get_defaults()
    
    def _load_yaml(self, config_path: str):
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to YAML file
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
                
                if yaml_config:
                    # Merge with existing config (YAML overrides defaults)
                    self._config.update(yaml_config)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format in {config_path}: {e}")
    
    def _load_env_variables(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'LANDGUARD_RAPID_TRANSFER_DAYS': ('rapid_transfer_days', int),
            'LANDGUARD_RAPID_TRANSFER_COUNT': ('rapid_transfer_count', int),
            'LANDGUARD_LARGE_TRANSFER_THRESHOLD': ('large_transfer_threshold', float),
            'LANDGUARD_NAME_SIMILARITY_THRESHOLD': ('name_similarity_threshold', float),
            'LANDGUARD_DATE_ORDER_TOLERANCE_DAYS': ('date_order_tolerance_days', int),
            'LANDGUARD_LOG_LEVEL': ('log_level', str),
            'LANDGUARD_OUTPUT_FORMAT': ('output_format', str),
            'LANDGUARD_ENABLE_VERBOSE': ('enable_verbose', lambda x: x.lower() == 'true'),
        }
        
        for env_var, (config_key, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    self._config[config_key] = converter(value)
                except (ValueError, TypeError) as e:
                    print(f"Warning: Invalid value for {env_var}: {e}")
    
    def _validate(self):
        """Validate configuration values."""
        validation_result = self._validator.validate(self._config)
        
        if not validation_result['valid']:
            errors = '\n'.join(validation_result['errors'])
            raise ValueError(f"Configuration validation failed:\n{errors}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value
        """
        return self._config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
        self._validate()
    
    def update(self, config: Dict[str, Any]):
        """
        Update multiple configuration values.
        
        Args:
            config: Dictionary of configuration values
        """
        self._config.update(config)
        self._validate()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self._config.copy()
    
    def save(self, output_path: str):
        """
        Save configuration to YAML file.
        
        Args:
            output_path: Path to save YAML file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)


# Global configuration instance
_global_config: Optional[ConfigLoader] = None


def load_config(config_path: Optional[str] = None) -> ConfigLoader:
    """
    Load global configuration.
    
    Args:
        config_path: Path to YAML config file (optional)
        
    Returns:
        ConfigLoader instance
    """
    global _global_config
    _global_config = ConfigLoader(config_path)
    return _global_config


def get_config() -> ConfigLoader:
    """
    Get global configuration instance.
    
    Returns:
        ConfigLoader instance
        
    Raises:
        RuntimeError: If configuration not loaded
    """
    global _global_config
    
    if _global_config is None:
        # Load default configuration
        _global_config = ConfigLoader()
    
    return _global_config