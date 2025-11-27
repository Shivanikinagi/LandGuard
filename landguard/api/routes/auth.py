"""
Authentication Routes
User login, registration, and token management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from database.models import User
from database.repositories import UserRepository
from database.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from api.models.requests import UserLoginRequest, UserCreateRequest
from api.models.responses import UserResponse, TokenResponse
from api.dependencies import get_current_user

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserCreateRequest,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if username already exists
    existing_user = UserRepository.get_by_username(db, request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = UserRepository.get_by_email(db, request.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        username=request.username,
        email=request.email,
        password_hash=get_password_hash(request.password),
        full_name=request.full_name,
        role=request.role,
        is_active=True
    )
    
    created_user = UserRepository.create(db, user)
    return created_user


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    # Get user by username
    user = UserRepository.get_by_username(db, form_data.username)
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout (client should discard token)"""
    return {"message": "Successfully logged out"}