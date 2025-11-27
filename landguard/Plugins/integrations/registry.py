"""
LandGuard Phase 11: Integration Registry
Manages all external integrations
"""

from typing import Dict, Any, Optional, List, Type
from datetime import datetime, timezone
import logging
import yaml
from pathlib import Path

from .base import BaseIntegration, IntegrationType, IntegrationStatus


logger = logging.getLogger(__name__)


class IntegrationRegistry:
    """
    Central registry for managing all integrations
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.integrations: Dict[str, BaseIntegration] = {}
        self.config_path = config_path or "integrations/config/integrations.yaml"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load integration configuration from YAML"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return {}
        
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def register(
        self,
        name: str,
        integration: BaseIntegration,
        auto_enable: bool = False
    ) -> None:
        """
        Register a new integration
        
        Args:
            name: Unique integration name
            integration: Integration instance
            auto_enable: Whether to enable immediately
        """
        if name in self.integrations:
            logger.warning(f"Integration '{name}' already registered, replacing")
        
        self.integrations[name] = integration
        logger.info(f"Registered integration: {name}")
        
        if auto_enable:
            integration.enable()
    
    def get(self, name: str) -> Optional[BaseIntegration]:
        """Get integration by name"""
        return self.integrations.get(name)
    
    def remove(self, name: str) -> bool:
        """Remove an integration"""
        if name in self.integrations:
            integration = self.integrations[name]
            integration.disable()
            del self.integrations[name]
            logger.info(f"Removed integration: {name}")
            return True
        return False
    
    def enable_integration(self, name: str) -> bool:
        """Enable an integration"""
        integration = self.get(name)
        if integration:
            return integration.enable()
        logger.error(f"Integration not found: {name}")
        return False
    
    def disable_integration(self, name: str) -> bool:
        """Disable an integration"""
        integration = self.get(name)
        if integration:
            integration.disable()
            return True
        logger.error(f"Integration not found: {name}")
        return False
    
    def list_integrations(
        self,
        integration_type: Optional[IntegrationType] = None,
        status: Optional[IntegrationStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        List all integrations
        
        Args:
            integration_type: Filter by type
            status: Filter by status
        
        Returns:
            List of integration info
        """
        results = []
        
        for name, integration in self.integrations.items():
            # Apply filters
            if integration_type and integration.integration_type != integration_type:
                continue
            if status and integration.status != status:
                continue
            
            results.append(integration.get_info())
        
        return results
    
    def get_active_integrations(self) -> List[BaseIntegration]:
        """Get all active integrations"""
        return [
            integration
            for integration in self.integrations.values()
            if integration.is_available()
        ]
    
    def get_by_type(self, integration_type: IntegrationType) -> List[BaseIntegration]:
        """Get all integrations of a specific type"""
        return [
            integration
            for integration in self.integrations.values()
            if integration.integration_type == integration_type
        ]
    
    def test_all(self) -> Dict[str, bool]:
        """Test all integrations"""
        results = {}
        
        for name, integration in self.integrations.items():
            try:
                results[name] = integration.test_connection()
            except Exception as e:
                logger.error(f"Test failed for {name}: {e}")
                results[name] = False
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics for all integrations"""
        total = len(self.integrations)
        active = len([i for i in self.integrations.values() if i.is_available()])
        
        stats_by_type = {}
        for int_type in IntegrationType:
            count = len(self.get_by_type(int_type))
            if count > 0:
                stats_by_type[int_type.value] = count
        
        total_requests = sum(
            i.stats['total_requests']
            for i in self.integrations.values()
        )
        
        successful_requests = sum(
            i.stats['successful_requests']
            for i in self.integrations.values()
        )
        
        return {
            'total_integrations': total,
            'active_integrations': active,
            'inactive_integrations': total - active,
            'integrations_by_type': stats_by_type,
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': (
                successful_requests / total_requests * 100
                if total_requests > 0 else 0
            ),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all integrations
        
        Returns:
            Health status for each integration
        """
        health = {}
        
        for name, integration in self.integrations.items():
            try:
                is_healthy = integration.test_connection()
                rate_limit = integration.get_rate_limit()
                
                health[name] = {
                    'healthy': is_healthy,
                    'status': integration.status.value,
                    'rate_limit': rate_limit,
                    'last_request': integration.stats.get('last_request'),
                    'last_error': integration.stats.get('last_error')
                }
            except Exception as e:
                health[name] = {
                    'healthy': False,
                    'status': 'error',
                    'error': str(e)
                }
        
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'integrations': health,
            'overall_health': all(h.get('healthy', False) for h in health.values())
        }
    
    def close_all(self) -> None:
        """Close all integrations"""
        for integration in self.integrations.values():
            try:
                if hasattr(integration, 'close'):
                    integration.close()
            except Exception as e:
                logger.error(f"Error closing integration: {e}")
        
        logger.info("All integrations closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_all()


# Global registry instance
_registry = IntegrationRegistry()


def get_registry() -> IntegrationRegistry:
    """Get the global integration registry"""
    return _registry


# Export
__all__ = ['IntegrationRegistry', 'get_registry']