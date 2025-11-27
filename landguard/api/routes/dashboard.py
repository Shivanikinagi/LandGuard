"""
Dashboard Routes
Dashboard statistics and overview endpoints
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
security = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User | None:
    """Get current user from token (optional)"""
    if not credentials:
        return None
    
    try:
        payload = decode_access_token(credentials.credentials)
        if not payload:
            return None
        
        username = payload.get("sub")
        if not username:
            return None
        
        user = db.query(User).filter(User.username == username).first()
        return user
    except Exception:
        return None


def get_current_user_required(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from token (required)"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.get("/public")
async def get_public_dashboard(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get public dashboard statistics (no authentication required)
    
    Returns:
        Public dashboard data
    """
    try:
        # Get total counts
        total_records = db.query(func.count(LandRecord.id)).scalar() or 0
        total_users = db.query(func.count(User.id)).scalar() or 0
        total_analyses = db.query(func.count(AnalysisResult.id)).scalar() or 0
        
        # Get fraud detection stats
        fraud_detected = db.query(func.count(AnalysisResult.id)).filter(
            AnalysisResult.fraud_detected == True
        ).scalar() or 0
        
        # Get anomaly detection stats
        anomaly_detected = db.query(func.count(AnalysisResult.id)).filter(
            AnalysisResult.anomaly_detected == True
        ).scalar() or 0
        
        # Calculate percentages
        fraud_percentage = (fraud_detected / total_analyses * 100) if total_analyses > 0 else 0
        anomaly_percentage = (anomaly_detected / total_analyses * 100) if total_analyses > 0 else 0
        
        return {
            "total_records": total_records,
            "total_users": total_users,
            "total_analyses": total_analyses,
            "fraud_detected": fraud_detected,
            "anomaly_detected": anomaly_detected,
            "fraud_percentage": round(fraud_percentage, 2),
            "anomaly_percentage": round(anomaly_percentage, 2),
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"Error getting public dashboard: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard data: {str(e)}"
        )


@router.get("/user")
async def get_user_dashboard(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get user-specific dashboard statistics
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        User dashboard data
    """
    try:
        # Get user's records
        user_records = db.query(func.count(LandRecord.id)).filter(
            LandRecord.user_id == current_user.id
        ).scalar() or 0
        
        # Get user's analyses
        user_analyses = db.query(func.count(AnalysisResult.id)).join(
            LandRecord
        ).filter(
            LandRecord.user_id == current_user.id
        ).scalar() or 0
        
        # Get fraud detected in user's records
        user_fraud = db.query(func.count(AnalysisResult.id)).join(
            LandRecord
        ).filter(
            LandRecord.user_id == current_user.id,
            AnalysisResult.fraud_detected == True
        ).scalar() or 0
        
        # Get recent records
        recent_records = db.query(LandRecord).filter(
            LandRecord.user_id == current_user.id
        ).order_by(LandRecord.created_at.desc()).limit(5).all()
        
        return {
            "user_id": current_user.id,
            "username": current_user.username,
            "total_records": user_records,
            "total_analyses": user_analyses,
            "fraud_detected": user_fraud,
            "recent_records": [
                {
                    "id": record.id,
                    "record_number": record.record_number,
                    "status": record.status,
                    "created_at": record.created_at.isoformat() if record.created_at else None
                }
                for record in recent_records
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting user dashboard: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user dashboard: {str(e)}"
        )


@router.get("/overview")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get dashboard overview (works with or without authentication)
    
    Args:
        current_user: Current user (optional)
        db: Database session
        
    Returns:
        Dashboard overview
    """
    try:
        if current_user:
            # Return user-specific dashboard
            return await get_user_dashboard(current_user, db)
        else:
            # Return public dashboard
            return await get_public_dashboard(db)
            
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard overview: {str(e)}"
        )


@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed dashboard statistics
    
    Args:
        db: Database session
        
    Returns:
        Detailed statistics
    """
    try:
        # Get status distribution
        status_counts = db.query(
            LandRecord.status,
            func.count(LandRecord.id)
        ).group_by(LandRecord.status).all()
        
        # Get risk assessment distribution
        risk_counts = db.query(
            AnalysisResult.risk_assessment,
            func.count(AnalysisResult.id)
        ).group_by(AnalysisResult.risk_assessment).all()
        
        return {
            "status_distribution": {
                status: count for status, count in status_counts
            },
            "risk_distribution": {
                risk: count for risk, count in risk_counts if risk
            },
            "total_records": db.query(func.count(LandRecord.id)).scalar() or 0,
            "total_analyses": db.query(func.count(AnalysisResult.id)).scalar() or 0
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get recent activity
    
    Args:
        limit: Maximum number of records
        current_user: Current user (optional)
        db: Database session
        
    Returns:
        Recent activity data
    """
    try:
        query = db.query(LandRecord)
        
        if current_user:
            # Filter by user
            query = query.filter(LandRecord.user_id == current_user.id)
        
        recent_records = query.order_by(
            LandRecord.created_at.desc()
        ).limit(limit).all()
        
        return {
            "records": [
                {
                    "id": record.id,
                    "record_number": record.record_number,
                    "status": record.status,
                    "owner_name": record.owner_name,
                    "created_at": record.created_at.isoformat() if record.created_at else None
                }
                for record in recent_records
            ],
            "total": len(recent_records)
        }
        
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent activity: {str(e)}"
        )