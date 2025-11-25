"""
Authentication and authorization for LandGuard.
Supports API key authentication and JWT tokens.
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False


class UserRole(Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class Permission(Enum):
    """Available permissions."""
    READ = "read"
    WRITE = "write"
    ANALYZE = "analyze"
    DELETE = "delete"
    ADMIN = "admin"


# Role-based permissions mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.READ,
        Permission.WRITE,
        Permission.ANALYZE,
        Permission.DELETE,
        Permission.ADMIN
    ],
    UserRole.ANALYST: [
        Permission.READ,
        Permission.WRITE,
        Permission.ANALYZE
    ],
    UserRole.VIEWER: [
        Permission.READ
    ]
}


class APIKeyAuth:
    """API Key authentication."""
    
    def __init__(self):
        """Initialize API key authentication."""
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self._load_keys_from_env()
    
    def _load_keys_from_env(self):
        """Load API keys from environment variables."""
        # Load from LANDGUARD_API_KEYS environment variable
        # Format: key1:role1,key2:role2
        keys_env = os.getenv('LANDGUARD_API_KEYS', '')
        
        if keys_env:
            for key_pair in keys_env.split(','):
                if ':' in key_pair:
                    key, role = key_pair.split(':', 1)
                    self.api_keys[key.strip()] = {
                        'role': UserRole(role.strip()),
                        'created_at': datetime.utcnow(),
                        'active': True
                    }
    
    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a secure API key.
        
        Returns:
            Generated API key
        """
        # Generate 32 bytes of random data
        random_bytes = secrets.token_bytes(32)
        
        # Create a hash and encode as hex
        key_hash = hashlib.sha256(random_bytes).hexdigest()
        
        # Format: lg_ prefix + first 40 chars of hash
        return f"lg_{key_hash[:40]}"
    
    def create_key(self, role: UserRole, description: Optional[str] = None) -> str:
        """
        Create a new API key.
        
        Args:
            role: User role for this key
            description: Optional description
            
        Returns:
            Generated API key
        """
        api_key = self.generate_api_key()
        
        self.api_keys[api_key] = {
            'role': role,
            'description': description,
            'created_at': datetime.utcnow(),
            'active': True,
            'last_used': None,
            'usage_count': 0
        }
        
        return api_key
    
    def validate_key(self, api_key: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate an API key.
        
        Args:
            api_key: API key to validate
            
        Returns:
            Tuple of (is_valid, key_info)
        """
        if not api_key or not isinstance(api_key, str):
            return False, None
        
        key_info = self.api_keys.get(api_key)
        
        if not key_info:
            return False, None
        
        if not key_info.get('active', False):
            return False, None
        
        # Update usage statistics
        key_info['last_used'] = datetime.utcnow()
        key_info['usage_count'] = key_info.get('usage_count', 0) + 1
        
        return True, key_info
    
    def revoke_key(self, api_key: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            api_key: API key to revoke
            
        Returns:
            True if revoked successfully
        """
        if api_key in self.api_keys:
            self.api_keys[api_key]['active'] = False
            return True
        return False
    
    def list_keys(self) -> List[Dict[str, Any]]:
        """
        List all API keys (excluding actual key values).
        
        Returns:
            List of key information
        """
        return [
            {
                'key_hash': hashlib.sha256(key.encode()).hexdigest()[:16],
                'role': info['role'].value,
                'description': info.get('description'),
                'created_at': info['created_at'].isoformat(),
                'active': info['active'],
                'last_used': info.get('last_used').isoformat() if info.get('last_used') else None,
                'usage_count': info.get('usage_count', 0)
            }
            for key, info in self.api_keys.items()
        ]


class JWTAuth:
    """JWT token authentication."""
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize JWT authentication.
        
        Args:
            secret_key: Secret key for JWT signing (loads from env if not provided)
        """
        if not JWT_AVAILABLE:
            raise ImportError(
                "PyJWT library not installed. "
                "Install with: pip install PyJWT"
            )
        
        self.secret_key = secret_key or os.getenv('LANDGUARD_JWT_SECRET')
        
        if not self.secret_key:
            # Generate a random secret if not provided
            self.secret_key = secrets.token_urlsafe(32)
        
        self.algorithm = 'HS256'
        self.token_expiry = timedelta(hours=24)
    
    def create_token(
        self,
        user_id: str,
        role: UserRole,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a JWT token.
        
        Args:
            user_id: User identifier
            role: User role
            additional_claims: Optional additional claims
            
        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        
        payload = {
            'user_id': user_id,
            'role': role.value,
            'iat': now,
            'exp': now + self.token_expiry,
            'nbf': now,
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        return token
    
    def verify_token(self, token: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Verify a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Tuple of (is_valid, payload)
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return True, payload
        
        except jwt.ExpiredSignatureError:
            return False, {'error': 'Token expired'}
        
        except jwt.InvalidTokenError:
            return False, {'error': 'Invalid token'}
        
        except Exception as e:
            return False, {'error': str(e)}
    
    def refresh_token(self, token: str) -> Optional[str]:
        """
        Refresh a JWT token.
        
        Args:
            token: Current JWT token
            
        Returns:
            New JWT token or None if invalid
        """
        is_valid, payload = self.verify_token(token)
        
        if not is_valid:
            return None
        
        # Create new token with same claims
        user_id = payload.get('user_id')
        role = UserRole(payload.get('role'))
        
        # Remove standard JWT claims
        additional_claims = {
            k: v for k, v in payload.items()
            if k not in ['user_id', 'role', 'iat', 'exp', 'nbf']
        }
        
        return self.create_token(user_id, role, additional_claims)


class AuthManager:
    """Unified authentication manager supporting multiple auth methods."""
    
    def __init__(self):
        """Initialize authentication manager."""
        self.api_key_auth = APIKeyAuth()
        
        try:
            self.jwt_auth = JWTAuth()
            self.jwt_enabled = True
        except ImportError:
            self.jwt_auth = None
            self.jwt_enabled = False
    
    def authenticate(
        self,
        credentials: str,
        auth_type: str = 'api_key'
    ) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Authenticate user with provided credentials.
        
        Args:
            credentials: API key or JWT token
            auth_type: Type of authentication ('api_key' or 'jwt')
            
        Returns:
            Tuple of (is_authenticated, user_info)
        """
        if auth_type == 'api_key':
            return self.api_key_auth.validate_key(credentials)
        
        elif auth_type == 'jwt' and self.jwt_enabled:
            is_valid, payload = self.jwt_auth.verify_token(credentials)
            
            if is_valid:
                user_info = {
                    'role': UserRole(payload['role']),
                    'user_id': payload['user_id']
                }
                return True, user_info
            
            return False, None
        
        else:
            return False, None
    
    def has_permission(self, role: UserRole, permission: Permission) -> bool:
        """
        Check if a role has a specific permission.
        
        Args:
            role: User role
            permission: Permission to check
            
        Returns:
            True if role has permission
        """
        role_perms = ROLE_PERMISSIONS.get(role, [])
        return permission in role_perms
    
    def require_permission(
        self,
        user_info: Dict[str, Any],
        permission: Permission
    ) -> tuple[bool, Optional[str]]:
        """
        Check if user has required permission.
        
        Args:
            user_info: User information from authentication
            permission: Required permission
            
        Returns:
            Tuple of (has_permission, error_message)
        """
        if not user_info:
            return False, "User not authenticated"
        
        role = user_info.get('role')
        
        if not role:
            return False, "User role not found"
        
        if self.has_permission(role, permission):
            return True, None
        
        return False, f"Permission denied: {permission.value} required"
    
    def create_api_key(
        self,
        role: UserRole,
        description: Optional[str] = None
    ) -> str:
        """
        Create a new API key (convenience method).
        
        Args:
            role: User role
            description: Optional description
            
        Returns:
            Generated API key
        """
        return self.api_key_auth.create_key(role, description)
    
    def create_jwt_token(
        self,
        user_id: str,
        role: UserRole,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a JWT token (convenience method).
        
        Args:
            user_id: User identifier
            role: User role
            additional_claims: Optional additional claims
            
        Returns:
            JWT token or None if JWT not enabled
        """
        if not self.jwt_enabled:
            return None
        
        return self.jwt_auth.create_token(user_id, role, additional_claims)