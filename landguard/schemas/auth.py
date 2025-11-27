"""
Auth Schemas
Pydantic models for authentication and authorization
"""

from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """JWT token data"""
    username: Optional[str] = None


class UserCreate(BaseModel):
    """User creation request"""
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    """User login request"""
    username: str
    password: str


class UserResponse(BaseModel):
    """User response"""
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True