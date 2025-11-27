"""
Statistics Routes
System statistics and analytics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
import logging

from database import get_db
from database.models import User, LandRecord, AnalysisResult
from database.auth import decode_access_token

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    # Log token info for debugging
    logger.info(f"Token received: {credentials.credentials[:20] if credentials.credentials else 'None'}...")
    
    if not credentials or not credentials.credentials:
        logger.error("No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = decode_access_token(credentials.credentials)
        logger.info(f"Token payload: {payload}")
        
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.error("No user ID in token payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        logger.info(f"Authenticated user: {user.username}")
        return user
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/overview")
async def get_statistics_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system statistics overview"""
    logger.info(f"Getting statistics overview for user: {current_user.username}")
    
    try:
        # Get total records
        total_records = db.query(LandRecord).count()
        
        # Get total users
        total_users = db.query(User).count()
        
        # Get fraud detected (assuming fraud_flag=True means fraud detected)
        fraud_detected = db.query(LandRecord).filter(LandRecord.fraud_flag == True).count()
        
        # Calculate fraud rate
        fraud_rate = (fraud_detected / total_records * 100) if total_records > 0 else 0
        
        result = {
            "total_records": total_records,
            "total_users": total_users,
            "fraud_detected": fraud_detected,
            "fraud_rate": round(fraud_rate, 2)
        }
        
        logger.info(f"Statistics overview result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error getting statistics overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )


@router.get("/trends")
async def get_statistics_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system statistics trends"""
    logger.info(f"Getting statistics trends for user: {current_user.username}")
    
    try:
        # For now, return dummy data - in a real implementation this would
        # return time-series data for charts
        result = {
            "fraud_trends": [],
            "risk_distribution": [],
            "recent_analyses": []
        }
        
        logger.info(f"Statistics trends result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error getting statistics trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trends"
        )