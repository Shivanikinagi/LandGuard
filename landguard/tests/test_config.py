"""
Unit tests for configuration system.
"""

import pytest
import os
import tempfile
import yaml
from pathlib import Path

from core.config import ConfigLoader, ConfigValidator, ConfigSchema, load_config, get_config


class TestConfigSchema:
    """Test configuration schema."""
    
    def test_get_defaults(self):
        """Test getting default configuration."""
        defaults = ConfigSchema.get_defaults()
        
        assert isinstance(defaults, dict)
        assert 'rapid_transfer_days' in defaults
        assert 'large_transfer_threshold' in defaults
        assert defaults['rapid_transfer_days'] == 180
        assert defaults['log_level'] == 'INFO'
    
    def test_get_schema(self):
        """Test getting configuration schema."""
        schema = ConfigSchema.get_schema()
        
        assert isinstance(schema, dict)
        assert 'rapid_transfer_days' in schema
        assert 'type' in schema['rapid_transfer_days']
        assert 'description' in schema['rapid_transfer_days']
    
    def test_generate_yaml_template(self):
        """Test YAML template generation."""
        template = ConfigSchema.generate_yaml_template()
        
        assert isinstance(template, str)
        assert 'rapid_transfer_days' in template
        assert 'Fraud Detection Settings' in template
        assert '#' in template  # Has comments


class TestConfigValidator:
    """Test configuration validator."""
    
    def test_validate_valid_config(self):
        """Test validation of valid configuration."""
        validator = ConfigValidator()
        
        config = {
            'rapid_transfer_days': 180,
            'rapid_transfer_count': 2,
            'large_transfer_threshold': 10000000,
            'log_level': 'INFO',
            'enable_verbose': False
        }
        
        result = validator.validate(config)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
    
    def test_validate_invalid_type(self):
        """Test validation with invalid type."""
        validator = ConfigValidator()
        
        config = {
            'rapid_transfer_days': "not_a_number"  # Should be int
        }
        
        result = validator.validate(config)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert 'Expected' in result['errors'][0]
    
    def test_validate_out_of_range(self):
        """Test validation with out-of-range value."""
        validator = ConfigValidator()
        
        config = {
            'rapid_transfer_days': 5000  # Exceeds max of 3650
        }
        
        result = validator.validate(config)
        
        assert result['valid'] is False
        assert 'exceeds maximum' in result['errors'][0]
    
    def test_validate_invalid_choice(self):
        """Test validation with invalid choice."""
        validator = ConfigValidator()
        
        config = {
            'log_level': 'INVALID_LEVEL'
        }
        
        result = validator.validate(config)
        
        assert result['valid'] is False
        assert 'not in allowed choices' in result['errors'][0]
    
    def test_validate_below_minimum(self):
        """Test validation with value below minimum."""
        validator = ConfigValidator()
        
        config = {
            'rapid_transfer_count': 0  # Below min of 2
        }
        
        result = validator.validate(config)
        
        assert result['valid'] is False
        assert 'below minimum' in result['errors'][0]
    
    def test_get_rule(self):
        """Test getting validation rule."""
        validator = ConfigValidator()
        
        rule = validator.get_rule('rapid_transfer_days')
        
        assert rule is not None
        assert 'type' in rule
        assert 'min' in rule
        assert 'max' in rule


class TestConfigLoader:
    """Test configuration loader."""
    
    def test_load_defaults(self):
        """Test loading default configuration."""
        config = ConfigLoader()
        
        assert config.get('rapid_transfer_days') == 180
        assert config.get('log_level') == 'INFO'
        assert config.get('enable_verbose') is False
    
    def test_load_yaml_file(self, tmp_path):
        """Test loading configuration from YAML file."""
        # Create test YAML file
        config_data = {
            'rapid_transfer_days': 90,
            'log_level': 'DEBUG',
            'enable_verbose': True
        }
        
        config_file = tmp_path / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        config = ConfigLoader(str(config_file))
        
        assert config.get('rapid_transfer_days') == 90
        assert config.get('log_level') == 'DEBUG'
        assert config.get('enable_verbose') is True
    
    def test_load_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML file."""
        config_file = tmp_path / "invalid.yaml"
        with open(config_file, 'w') as f:
            f.write("invalid: yaml: content:")
        
        with pytest.raises(ValueError, match="Invalid YAML format"):
            ConfigLoader(str(config_file))
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent configuration file."""
        with pytest.raises(FileNotFoundError):
            ConfigLoader("/path/to/nonexistent/config.yaml")
    
    def test_load_env_variables(self, monkeypatch):
        """Test loading configuration from environment variables."""
        # Set environment variables
        monkeypatch.setenv('LANDGUARD_RAPID_TRANSFER_DAYS', '120')
        monkeypatch.setenv('LANDGUARD_LOG_LEVEL', 'DEBUG')
        monkeypatch.setenv('LANDGUARD_ENABLE_VERBOSE', 'true')
        
        config = ConfigLoader()
        
        assert config.get('rapid_transfer_days') == 120
        assert config.get('log_level') == 'DEBUG'
        assert config.get('enable_verbose') is True
    
    def test_env_overrides_yaml(self, tmp_path, monkeypatch):
        """Test that environment variables override YAML config."""
        # Create YAML file
        config_data = {'rapid_transfer_days': 90}
        config_file = tmp_path / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Set environment variable
        monkeypatch.setenv('LANDGUARD_RAPID_TRANSFER_DAYS', '200')
        
        config = ConfigLoader(str(config_file))
        
        # Env var should override YAML
        assert config.get('rapid_transfer_days') == 200
    
    def test_get_nonexistent_key(self):
        """Test getting non-existent configuration key."""
        config = ConfigLoader()
        
        assert config.get('nonexistent_key') is None
        assert config.get('nonexistent_key', 'default_value') == 'default_value'
    
    def test_set_config_value(self):
        """Test setting configuration value."""
        config = ConfigLoader()
        
        config.set('rapid_transfer_days', 250)
        
        assert config.get('rapid_transfer_days') == 250
    
    def test_set_invalid_value(self):
        """Test setting invalid configuration value."""
        config = ConfigLoader()
        
        with pytest.raises(ValueError, match="validation failed"):
            config.set('rapid_transfer_days', 10000)  # Exceeds max
    
    def test_update_config(self):
        """Test updating multiple configuration values."""
        config = ConfigLoader()
        
        config.update({
            'rapid_transfer_days': 120,
            'log_level': 'WARNING'
        })
        
        assert config.get('rapid_transfer_days') == 120
        assert config.get('log_level') == 'WARNING'
    
    def test_get_all_config(self):
        """Test getting all configuration values."""
        config = ConfigLoader()
        
        all_config = config.get_all()
        
        assert isinstance(all_config, dict)
        assert 'rapid_transfer_days' in all_config
        assert 'log_level' in all_config
    
    def test_to_dict(self):
        """Test converting configuration to dictionary."""
        config = ConfigLoader()
        
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict == config.get_all()
    
    def test_save_config(self, tmp_path):
        """Test saving configuration to file."""
        config = ConfigLoader()
        config.set('rapid_transfer_days', 150)
        
        output_file = tmp_path / "saved_config.yaml"
        config.save(str(output_file))
        
        assert output_file.exists()
        
        # Load and verify
        with open(output_file, 'r') as f:
            saved_data = yaml.safe_load(f)
        
        assert saved_data['rapid_transfer_days'] == 150


class TestGlobalConfig:
    """Test global configuration functions."""
    
    def test_load_global_config(self):
        """Test loading global configuration."""
        config = load_config()
        
        assert isinstance(config, ConfigLoader)
        assert config.get('rapid_transfer_days') is not None
    
    def test_get_global_config(self):
        """Test getting global configuration."""
        load_config()  # Initialize
        config = get_config()
        
        assert isinstance(config, ConfigLoader)
    
    def test_get_config_without_load(self):
        """Test getting config without explicit load (should auto-initialize)."""
        # Reset global config
        import core.config.config_loader
        core.config.config_loader._global_config = None
        
        config = get_config()
        
        assert isinstance(config, ConfigLoader)


class TestConfigIntegration:
    """Integration tests for configuration system."""
    
    def test_full_workflow(self, tmp_path):
        """Test complete configuration workflow."""
        # Create custom config
        config_data = {
            'rapid_transfer_days': 100,
            'rapid_transfer_count': 3,
            'log_level': 'WARNING'
        }
        
        config_file = tmp_path / "workflow_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Load config
        config = ConfigLoader(str(config_file))
        
        # Verify loaded values
        assert config.get('rapid_transfer_days') == 100
        assert config.get('rapid_transfer_count') == 3
        assert config.get('log_level') == 'WARNING'
        
        # Modify and save
        config.set('rapid_transfer_days', 120)
        
        output_file = tmp_path / "modified_config.yaml"
        config.save(str(output_file))
        
        # Load modified config
        config2 = ConfigLoader(str(output_file))
        assert config2.get('rapid_transfer_days') == 120
    
    def test_yaml_env_priority(self, tmp_path, monkeypatch):
        """Test priority: env vars > YAML > defaults."""
        # Create YAML
        yaml_data = {'rapid_transfer_days': 150}
        config_file = tmp_path / "priority_test.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(yaml_data, f)
        
        # Set env var
        monkeypatch.setenv('LANDGUARD_RAPID_TRANSFER_DAYS', '200')
        
        config = ConfigLoader(str(config_file))
        
        # Env var should win
        assert config.get('rapid_transfer_days') == 200
        
        # Unset env var
        monkeypatch.delenv('LANDGUARD_RAPID_TRANSFER_DAYS')
        
        # Reload - YAML should win
        config2 = ConfigLoader(str(config_file))
        assert config2.get('rapid_transfer_days') == 150