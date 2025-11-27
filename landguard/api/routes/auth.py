"""
Auth Routes
User authentication and authorization endpoints
"""

import os
import sys
from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import get_db
from database.models import User
from database.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas.auth import Token

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint for user authentication"""
    logger.info(f"Login attempt for user: {form_data.username}")
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    logger.info(f"Successful login for user: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login/form", response_model=Token)
async def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint for OAuth2 form data support"""
    logger.info(f"Form login attempt for user: {form_data.username}")
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed form login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    logger.info(f"Successful form login for user: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}
