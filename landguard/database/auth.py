"""
Authentication Module
Password hashing, token generation, and user authentication
"""

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password from database
        
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing token data (usually {"sub": username})
        expires_delta: Optional expiration time delta
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """
    Decode and validate a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Optional[str]: Username from token if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token with longer expiration
    
    Args:
        data: Dictionary containing token data
        
    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # 7 days for refresh token
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> bool:
    """
    Verify if a token is valid
    
    Args:
        token: JWT token string
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    return decode_access_token(token) is not None


def authenticate_user(username: str, password: str, user) -> bool:
    """
    Authenticate a user with username and password
    
    Args:
        username: Username
        password: Plain text password
        user: User object from database
        
    Returns:
        bool: True if authentication successful, False otherwise
    """
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return True


def check_password_strength(password: str) -> tuple[bool, str]:
    """
    Check if password meets strength requirements
    
    Args:
        password: Plain text password
        
    Returns:
        tuple[bool, str]: (is_strong, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and numbers"
    
    return True, "Password is strong"


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key
    
    Args:
        api_key: Plain API key
        
    Returns:
        str: Hashed API key
    """
    return get_password_hash(api_key)


def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """
    Verify an API key
    
    Args:
        plain_api_key: Plain API key
        hashed_api_key: Hashed API key from database
        
    Returns:
        bool: True if API key matches, False otherwise
    """
    return verify_password(plain_api_key, hashed_api_key)