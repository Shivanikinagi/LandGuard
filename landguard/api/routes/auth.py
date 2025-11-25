"""
Authentication endpoints.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from api.models.requests import TokenRequest, TokenRefreshRequest
from api.models.responses import TokenResponse, UserInfoResponse, ErrorResponse
from api.dependencies import get_current_user, auth_manager, audit_logger
from core.security.auth import UserRole

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/token", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
async def create_token(request: TokenRequest):
    """
    Create JWT token for authentication.
    
    For demo purposes, accepts any username with password length >= 8.
    In production, verify against a user database.
    """
    # Demo authentication - replace with real user verification
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Determine role based on username (demo logic)
    if "admin" in request.username.lower():
        role = UserRole.ADMIN
    elif "analyst" in request.username.lower():
        role = UserRole.ANALYST
    else:
        role = UserRole.VIEWER
    
    # Create JWT token
    if not auth_manager.jwt_enabled:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="JWT authentication not available"
        )
    
    token = auth_manager.create_jwt_token(
        user_id=request.username,
        role=role
    )
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create token"
        )
    
    # Log successful token creation
    audit_logger.log_authentication(
        user_id=request.username,
        ip_address="unknown",  # Will be set by middleware
        success=True,
        auth_method="jwt_creation"
    )
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=86400,  # 24 hours
        refresh_token=None  # Implement refresh tokens if needed
    )


@router.post("/refresh", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
async def refresh_token(request: TokenRefreshRequest):
    """
    Refresh an expired JWT token.
    """
    if not auth_manager.jwt_enabled:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="JWT authentication not available"
        )
    
    new_token = auth_manager.jwt_auth.refresh_token(request.refresh_token)
    
    if not new_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return TokenResponse(
        access_token=new_token,
        token_type="bearer",
        expires_in=86400
    )


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information.
    """
    role = user.get('role')
    
    # Get permissions for role
    from core.security.auth import ROLE_PERMISSIONS
    permissions = [p.value for p in ROLE_PERMISSIONS.get(role, [])]
    
    return UserInfoResponse(
        user_id=user.get('user_id', 'unknown'),
        role=role.value if hasattr(role, 'value') else str(role),
        permissions=permissions
    )


@router.post("/api-key/create", response_model=dict)
async def create_api_key(
    role: str,
    description: str = None,
    user: dict = Depends(get_current_user)
):
    """
    Create a new API key (admin only).
    """
    # Check if user is admin
    if user.get('role') != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        user_role = UserRole(role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {role}"
        )
    
    api_key = auth_manager.create_api_key(user_role, description)
    
    # Log API key creation
    audit_logger.log_event(
        audit_logger.logger.makeRecord(
            name='security.api_key',
            level=20,  # INFO
            fn='',
            lno=0,
            msg=f'API key created for role {role}',
            args=(),
            exc_info=None
        )
    )
    
    return {
        "api_key": api_key,
        "role": role,
        "description": description,
        "created_at": datetime.utcnow().isoformat()
    }


@router.get("/api-keys", response_model=list)
async def list_api_keys(user: dict = Depends(get_current_user)):
    """
    List all API keys (admin only).
    """
    # Check if user is admin
    if user.get('role') != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return auth_manager.api_key_auth.list_keys()