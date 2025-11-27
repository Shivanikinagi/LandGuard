"""
Authentication Utilities
Password hashing, JWT token generation, and API key management
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    """
    Authenticate a user by username and password

    Args:
        db: Database session
        username: Username to authenticate
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    from database.models import User  # Import here to avoid circular imports
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT access token

    Args:
        token: JWT access token to decode

    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Check if it's an access token
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token

    Args:
        data: Data to encode in the token

    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # 7 days for refresh tokens
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT refresh token

    Args:
        token: JWT refresh token to decode

    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Check if it's a refresh token
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


def generate_password_reset_token(email: str) -> str:
    """
    Generate a password reset token

    Args:
        email: User's email address

    Returns:
        Password reset token
    """
    data = {
        "sub": email,
        "type": "password_reset"
    }
    expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour for reset tokens
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token

    Args:
        token: Password reset token

    Returns:
        Email address if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def create_email_verification_token(email: str) -> str:
    """
    Generate an email verification token

    Args:
        email: User's email address

    Returns:
        Email verification token
    """
    data = {
        "sub": email,
        "type": "email_verification"
    }
    expire = datetime.utcnow() + timedelta(days=1)  # 24 hours for verification
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_email_verification_token(token: str) -> Optional[str]:
    """
    Verify an email verification token

    Args:
        token: Email verification token

    Returns:
        Email address if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "email_verification":
            return None
        return payload.get("sub")
    except JWTError:
        return None


def generate_secure_random_string(length: int = 32) -> str:
    """
    Generate a cryptographically secure random string

    Args:
        length: Length of the random string

    Returns:
        Random string
    """
    return secrets.token_urlsafe(length)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"
    return True, "Password is strong"


def create_api_key(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create an API key for a user

    Args:
        user_id: User ID
        expires_delta: Expiration time

    Returns:
        API key
    """
    data = {
        "sub": user_id,
        "type": "api_key"
    }
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=365)  # 1 year default
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """
    Verify an API key

    Args:
        api_key: API key to verify

    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(api_key, SECRET_KEY, algorithms=[ALGORITHM])
        # Check if it's an API key
        if payload.get("type") != "api_key":
            return None
        return payload
    except JWTError:
        return None