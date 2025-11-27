"""
LandGuard Phase 11: Base Integration Class
Provides common functionality for all integrations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import logging
from enum import Enum


class IntegrationStatus(Enum):
    """Integration connection status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    DISABLED = "disabled"


class IntegrationType(Enum):
    """Types of integrations"""
    GOVERNMENT = "government"
    KYC = "kyc"
    VALUATION = "valuation"
    PAYMENT = "payment"
    AUDIT = "audit"
    LEGAL = "legal"


class BaseIntegration(ABC):
    """
    Base class for all external integrations
    Provides common functionality like authentication, error handling, logging
    """
    
    def __init__(
        self,
        name: str,
        integration_type: IntegrationType,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 30,
        retry_attempts: int = 3
    ):
        self.name = name
        self.integration_type = integration_type
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.status = IntegrationStatus.INACTIVE
        self.logger = logging.getLogger(f"landguard.integrations.{name}")
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "last_request": None,
            "last_error": None
        }
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the external service
        Returns True if authentication successful
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test connection to the service
        Returns True if connection successful
        """
        pass
    
    @abstractmethod
    def get_rate_limit(self) -> Dict[str, int]:
        """
        Get current rate limit status
        Returns dict with limit, remaining, reset info
        """
        pass
    
    def is_available(self) -> bool:
        """Check if integration is available and active"""
        return self.status == IntegrationStatus.ACTIVE
    
    def enable(self) -> bool:
        """Enable the integration"""
        try:
            if self.authenticate() and self.test_connection():
                self.status = IntegrationStatus.ACTIVE
                self.logger.info(f"Integration '{self.name}' enabled")
                return True
            else:
                self.status = IntegrationStatus.ERROR
                self.logger.error(f"Failed to enable integration '{self.name}'")
                return False
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            self.logger.error(f"Error enabling integration: {e}")
            return False
    
    def disable(self) -> None:
        """Disable the integration"""
        self.status = IntegrationStatus.DISABLED
        self.logger.info(f"Integration '{self.name}' disabled")
    
    def record_request(self, success: bool, error: Optional[str] = None) -> None:
        """Record statistics for a request"""
        self.stats["total_requests"] += 1
        self.stats["last_request"] = datetime.now(timezone.utc).isoformat()
        
        if success:
            self.stats["successful_requests"] += 1
        else:
            self.stats["failed_requests"] += 1
            self.stats["last_error"] = error
    
    def get_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        return {
            "name": self.name,
            "type": self.integration_type.value,
            "status": self.status.value,
            "statistics": self.stats.copy()
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Get integration information"""
        return {
            "name": self.name,
            "type": self.integration_type.value,
            "status": self.status.value,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, status={self.status.value})>"


class IntegrationError(Exception):
    """Base exception for integration errors"""
    
    def __init__(self, message: str, integration_name: str, details: Optional[Dict] = None):
        self.message = message
        self.integration_name = integration_name
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(IntegrationError):
    """Authentication failed"""
    pass


class RateLimitError(IntegrationError):
    """Rate limit exceeded"""
    pass


class APIError(IntegrationError):
    """API request error"""
    pass


class ValidationError(IntegrationError):
    """Data validation error"""
    pass


# Export all classes
__all__ = [
    'BaseIntegration',
    'IntegrationStatus',
    'IntegrationType',
    'IntegrationError',
    'AuthenticationError',
    'RateLimitError',
    'APIError',
    'ValidationError'
]