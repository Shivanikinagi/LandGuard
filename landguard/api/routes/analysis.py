"""
Analysis endpoints for land fraud detection.
"""

import uuid
import time
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from api.models.requests import LandRecordRequest, BatchAnalysisRequest
from api.models.responses import (
    AnalysisResultResponse,
    BatchAnalysisResultResponse,
    FraudIndicatorResponse,
    ErrorResponse
)
from api.dependencies import (
    get_current_user,
    get_analyst_user,
    check_rate_limit,
    audit_logger
)
from core.analyzer import LandGuardAnalyzer
from core.models import LandRecord, OwnerHistory, Transaction, AnomalyReport
from core.security.validator import SecurityValidator
from core.security.sanitizer import DataSanitizer

router = APIRouter(prefix="/api/v1", tags=["analysis"])

# Initialize analyzer
analyzer = LandGuardAnalyzer()


def convert_request_to_model(request: LandRecordRequest) -> LandRecord:
    """Convert API request to internal model."""
    # Validate and sanitize inputs
    is_valid, errors = SecurityValidator.validate_record_dict(request.dict())
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "errors": errors}
        )
    
    # Sanitize data
    sanitized_data = DataSanitizer.sanitize_land_record(request.dict())
    
    # Convert to internal models
    owner_history = [
        OwnerHistory(
            owner_name=owner.owner_name,
            date=datetime.fromisoformat(owner.date)
        )
        for owner in request.owner_history
    ]
    
    transactions = [
        Transaction(
            from_party=tx.from_party,
            to_party=tx.to_party,
            date=datetime.fromisoformat(tx.date),
            amount=tx.amount
        )
        for tx in (request.transactions or [])
    ]
    
    return LandRecord(
        land_id=sanitized_data['land_id'],
        owner_history=owner_history,
        transactions=transactions
    )


def convert_result_to_response(land_id: str, result) -> AnalysisResultResponse:
    """Convert analysis result to API response."""
    # Handle both dict and AnomalyReport
    if isinstance(result, AnomalyReport):
        result_dict = result.to_dict()
    else:
        result_dict = result
    
    fraud_indicators = [
        FraudIndicatorResponse(
            type=indicator['type'],
            severity=indicator['severity'],
            confidence=indicator.get('confidence', 0.8),
            description=indicator.get('description', ''),
            details=indicator.get('details', {})
        )
        for indicator in result_dict.get('fraud_indicators', [])
    ]
    
    return AnalysisResultResponse(
        land_id=land_id,
        fraud_detected=result_dict.get('fraud_detected', False),
        risk_score=result_dict.get('risk_score', 0.0),
        fraud_indicators=fraud_indicators,
        analysis_timestamp=datetime.utcnow(),
        metadata=result_dict.get('metadata', {})
    )


@router.post(
    "/analyze",
    response_model=AnalysisResultResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    dependencies=[Depends(check_rate_limit)]
)
async def analyze_land_record(
    request: LandRecordRequest,
    user: dict = Depends(get_analyst_user)
):
    """
    Analyze a single land record for fraud indicators.
    
    Requires analyst or admin role.
    """
    try:
        # Convert request to model
        land_record = convert_request_to_model(request)
        
        # Perform analysis
        result = analyzer.analyze_record(land_record)
        
        # Convert to dict if it's an AnomalyReport
        if isinstance(result, AnomalyReport):
            result_dict = result.to_dict()
        else:
            result_dict = result
        
        # Log analysis
        audit_logger.log_data_access(
            user_id=user.get('user_id', 'unknown'),
            ip_address="unknown",  # Set by middleware
            resource=f"land_record:{request.land_id}",
            action="analyze",
            details={
                'fraud_detected': result_dict.get('fraud_detected', False),
                'risk_score': result_dict.get('risk_score', 0.0)
            }
        )
        
        # Convert result to response
        return convert_result_to_response(request.land_id, result_dict)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post(
    "/batch",
    response_model=BatchAnalysisResultResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    dependencies=[Depends(check_rate_limit)]
)
async def batch_analyze(
    request: BatchAnalysisRequest,
    user: dict = Depends(get_analyst_user)
):
    """
    Analyze multiple land records in batch.
    
    Requires analyst or admin role.
    Maximum 100 records per batch.
    """
    start_time = time.time()
    batch_id = str(uuid.uuid4())
    
    try:
        # Validate batch size
        if len(request.records) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 100 records per batch"
            )
        
        results = []
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        
        # Process each record
        for record_request in request.records:
            try:
                # Convert and analyze
                land_record = convert_request_to_model(record_request)
                result = analyzer.analyze_record(land_record)
                
                # Convert to dict if it's an AnomalyReport
                if isinstance(result, AnomalyReport):
                    result_dict = result.to_dict()
                else:
                    result_dict = result
                
                # Count risk levels
                risk_score = result_dict.get('risk_score', 0.0)
                if risk_score >= 70:
                    high_risk += 1
                elif risk_score >= 40:
                    medium_risk += 1
                else:
                    low_risk += 1
                
                # Convert to response
                results.append(convert_result_to_response(record_request.land_id, result_dict))
            
            except Exception as e:
                # Log individual record failure but continue batch
                audit_logger.log_suspicious_activity(
                    user_id=user.get('user_id'),
                    ip_address="unknown",
                    activity_type='batch_record_error',
                    details={
                        'batch_id': batch_id,
                        'land_id': record_request.land_id,
                        'error': str(e)
                    }
                )
        
        processing_time = time.time() - start_time
        
        # Log batch analysis
        audit_logger.log_data_access(
            user_id=user.get('user_id', 'unknown'),
            ip_address="unknown",
            resource=f"batch_analysis:{batch_id}",
            action="batch_analyze",
            details={
                'total_records': len(request.records),
                'processed': len(results),
                'high_risk': high_risk,
                'processing_time': processing_time
            }
        )
        
        return BatchAnalysisResultResponse(
            total_records=len(request.records),
            records_analyzed=len(results),
            high_risk_count=high_risk,
            medium_risk_count=medium_risk,
            low_risk_count=low_risk,
            results=results,
            processing_time_seconds=round(processing_time, 3),
            batch_id=batch_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch analysis failed: {str(e)}"
        )


@router.get("/reports/{batch_id}", response_model=BatchAnalysisResultResponse)
async def get_batch_report(
    batch_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Get batch analysis report by ID.
    
    Note: This is a placeholder. In production, store results in a database.
    """
    # TODO: Implement report storage and retrieval
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Report retrieval not yet implemented"
    )