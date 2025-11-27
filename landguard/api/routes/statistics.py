"""
Statistics and Dashboard Routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from database.connection import get_db
from database.models import LandRecord, Analysis
from api.routes.auth import get_current_user

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dashboard statistics"""
    
    # Total records
    total_records = db.query(func.count(LandRecord.id)).scalar() or 0
    
    # Total analyses
    total_analyses = db.query(func.count(Analysis.id)).scalar() or 0
    
    # Flagged records (high risk)
    flagged_records = db.query(func.count(Analysis.id)).filter(
        Analysis.risk_level == "HIGH"
    ).scalar() or 0
    
    # Risk level distribution
    high_risk = db.query(func.count(Analysis.id)).filter(
        Analysis.risk_level == "HIGH"
    ).scalar() or 0
    
    medium_risk = db.query(func.count(Analysis.id)).filter(
        Analysis.risk_level == "MEDIUM"
    ).scalar() or 0
    
    low_risk = db.query(func.count(Analysis.id)).filter(
        Analysis.risk_level == "LOW"
    ).scalar() or 0
    
    # Calculate fraud percentage
    fraud_percentage = (flagged_records / total_records * 100) if total_records > 0 else 0
    
    # Recent analyses
    recent_analyses = db.query(Analysis).order_by(
        Analysis.created_at.desc()
    ).limit(5).all()
    
    recent_analyses_data = []
    for analysis in recent_analyses:
        land_record = db.query(LandRecord).filter(
            LandRecord.id == analysis.land_record_id
        ).first()
        
        recent_analyses_data.append({
            "id": analysis.id,
            "land_record_id": land_record.record_number if land_record else "N/A",
            "risk_level": analysis.risk_level,
            "fraud_probability": analysis.fraud_probability,
            "created_at": analysis.created_at.isoformat(),
            "location": land_record.location if land_record else "Unknown"
        })
    
    # Fraud trends (last 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    
    fraud_trends = []
    for i in range(6):
        month_start = six_months_ago + timedelta(days=30 * i)
        month_end = month_start + timedelta(days=30)
        
        count = db.query(func.count(Analysis.id)).filter(
            Analysis.created_at >= month_start,
            Analysis.created_at < month_end,
            Analysis.risk_level == "HIGH"
        ).scalar() or 0
        
        fraud_trends.append({
            "month": month_start.strftime("%b"),
            "count": count
        })
    
    # Risk distribution for chart
    risk_distribution = [
        {"name": "High Risk", "value": high_risk, "color": "#f44336"},
        {"name": "Medium Risk", "value": medium_risk, "color": "#ff9800"},
        {"name": "Low Risk", "value": low_risk, "color": "#4caf50"}
    ]
    
    return {
        "statistics": {
            "total_records": total_records,
            "flagged_records": flagged_records,
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk,
            "fraud_percentage": round(fraud_percentage, 2)
        },
        "recent_analyses": recent_analyses_data,
        "fraud_trends": fraud_trends,
        "risk_distribution": risk_distribution
    }