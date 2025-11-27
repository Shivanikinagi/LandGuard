"""
Analysis Routes
ML-based fraud detection and analysis endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
import random

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
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.get("/models")
async def get_ml_models_status(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get ML models availability status
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Models status
    """
    return {
        "available": True,
        "models": {
            "fraud_detection": {
                "loaded": True,
                "version": "1.0",
                "accuracy": 0.92
            },
            "anomaly_detection": {
                "loaded": True,
                "version": "1.0",
                "accuracy": 0.89
            }
        },
        "message": "ML models are available (simulated)"
    }


@router.post("/analyze/{record_id}")
async def analyze_document(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze a document for fraud and anomalies
    
    Args:
        record_id: Land record ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Analysis results
    """
    try:
        # Get record
        record = db.query(LandRecord).filter(
            LandRecord.id == record_id,
            LandRecord.user_id == current_user.id
        ).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found"
            )
        
        # Simulate ML analysis (replace with actual ML model)
        fraud_score = random.uniform(0.0, 1.0)
        fraud_detected = fraud_score > 0.7
        anomaly_score = random.uniform(0.0, 1.0)
        anomaly_detected = anomaly_score > 0.6
        
        # Determine risk assessment
        if fraud_detected or anomaly_detected:
            risk_assessment = "high" if fraud_score > 0.85 else "medium"
        else:
            risk_assessment = "low"
        
        # Create analysis result
        analysis = AnalysisResult(
            land_record_id=record_id,
            fraud_detected=fraud_detected,
            fraud_score=round(fraud_score, 4),
            fraud_indicators={"simulated": True, "score": fraud_score},
            anomaly_detected=anomaly_detected,
            anomaly_score=round(anomaly_score, 4),
            anomaly_types={"simulated": True} if anomaly_detected else None,
            risk_assessment=risk_assessment,
            confidence_score=random.uniform(0.8, 0.99),
            analyzed_by=current_user.id,
            model_version="1.0"
        )
        
        db.add(analysis)
        
        # Update record status
        record.status = "analyzed"
        
        db.commit()
        db.refresh(analysis)
        
        logger.info(f"Analysis completed for record {record_id}")
        
        return {
            "id": analysis.id,
            "land_record_id": record_id,
            "fraud_detected": fraud_detected,
            "fraud_score": fraud_score,
            "anomaly_detected": anomaly_detected,
            "anomaly_score": anomaly_score,
            "risk_assessment": risk_assessment,
            "confidence_score": analysis.confidence_score,
            "message": "Analysis completed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing document: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/result/{analysis_id}")
async def get_analysis_result(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get analysis result by ID
    
    Args:
        analysis_id: Analysis result ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Analysis result
    """
    try:
        analysis = db.query(AnalysisResult).join(
            LandRecord
        ).filter(
            AnalysisResult.id == analysis_id,
            LandRecord.user_id == current_user.id
        ).first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analysis result not found"
            )
        
        return {
            "id": analysis.id,
            "land_record_id": analysis.land_record_id,
            "fraud_detected": analysis.fraud_detected,
            "fraud_score": analysis.fraud_score,
            "fraud_indicators": analysis.fraud_indicators,
            "anomaly_detected": analysis.anomaly_detected,
            "anomaly_score": analysis.anomaly_score,
            "anomaly_types": analysis.anomaly_types,
            "risk_assessment": analysis.risk_assessment,
            "confidence_score": analysis.confidence_score,
            "model_version": analysis.model_version,
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis result: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis result: {str(e)}"
        )


@router.get("/records/{record_id}/analyses")
async def get_record_analyses(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all analyses for a specific record
    
    Args:
        record_id: Land record ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of analyses
    """
    try:
        # Verify record ownership
        record = db.query(LandRecord).filter(
            LandRecord.id == record_id,
            LandRecord.user_id == current_user.id
        ).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found"
            )
        
        # Get analyses
        analyses = db.query(AnalysisResult).filter(
            AnalysisResult.land_record_id == record_id
        ).all()
        
        return [
            {
                "id": analysis.id,
                "fraud_detected": analysis.fraud_detected,
                "fraud_score": analysis.fraud_score,
                "anomaly_detected": analysis.anomaly_detected,
                "risk_assessment": analysis.risk_assessment,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None
            }
            for analysis in analyses
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting record analyses: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analyses: {str(e)}"
        )