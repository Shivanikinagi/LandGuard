"""
Analysis Routes
Endpoints for land record analysis
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from database.models import LandRecord, Analysis, User
from database.repositories import LandRecordRepository, AnalysisRepository
from api.models.requests import (
    LandRecordCreateRequest,
    AnalysisCreateRequest,
    BatchAnalysisRequest
)
from api.models.responses import (
    LandRecordResponse,
    AnalysisResponse,
    SuccessResponse,
    PaginatedResponse
)
from api.dependencies import get_current_user

router = APIRouter()


@router.post("/land-records", response_model=LandRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_land_record(
    request: LandRecordCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new land record"""
    # Check if record number already exists
    existing = LandRecordRepository.get_by_record_number(db, request.record_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Record number already exists"
        )
    
    # Create new land record
    land_record = LandRecord(
        record_number=request.record_number,
        owner_name=request.owner_name,
        location=request.location,
        area=request.area,
        status=request.status
    )
    
    created_record = LandRecordRepository.create(db, land_record)
    return created_record


@router.get("/land-records", response_model=List[LandRecordResponse])
async def get_land_records(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all land records with optional filtering"""
    records = LandRecordRepository.get_all(db, skip=skip, limit=limit, status=status_filter)
    return records


@router.get("/land-records/{record_id}", response_model=LandRecordResponse)
async def get_land_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific land record by ID"""
    record = LandRecordRepository.get_by_id(db, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land record not found"
        )
    return record


@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis(
    request: AnalysisCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new analysis for a land record"""
    # Check if land record exists
    land_record = LandRecordRepository.get_by_id(db, request.land_record_id)
    if not land_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land record not found"
        )
    
    # Create analysis
    analysis = Analysis(
        land_record_id=request.land_record_id,
        risk_level=request.risk_level,
        fraud_probability=request.fraud_probability,
        flags=request.flags,
        recommendation=request.recommendation,
        analyzed_by=request.analyzed_by or current_user.username
    )
    
    created_analysis = AnalysisRepository.create(db, analysis)
    
    # Update land record status
    land_record.status = "ANALYZED"
    db.commit()
    
    return created_analysis


@router.get("/analyze/{land_record_id}", response_model=List[AnalysisResponse])
async def get_analyses(
    land_record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all analyses for a specific land record"""
    analyses = AnalysisRepository.get_by_land_record(db, land_record_id)
    return analyses


@router.post("/batch-analyze", response_model=SuccessResponse)
async def batch_analyze(
    request: BatchAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Batch analyze multiple land records"""
    results = []
    
    for land_record_id in request.land_record_ids:
        # Check if land record exists
        land_record = LandRecordRepository.get_by_id(db, land_record_id)
        if not land_record:
            results.append({
                "id": land_record_id,
                "status": "failed",
                "reason": "Record not found"
            })
            continue
        
        # Create placeholder analysis
        analysis = Analysis(
            land_record_id=land_record_id,
            risk_level="PENDING",
            fraud_probability=0.0,
            flags=["Batch analysis queued"],
            analyzed_by=current_user.username
        )
        
        try:
            AnalysisRepository.create(db, analysis)
            results.append({
                "id": land_record_id,
                "status": "queued"
            })
        except Exception as e:
            results.append({
                "id": land_record_id,
                "status": "failed",
                "reason": str(e)
            })
    
    return SuccessResponse(
        message=f"Batch analysis queued for {len(request.land_record_ids)} records",
        data={"results": results}
    )