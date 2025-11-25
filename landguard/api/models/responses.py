"""
API response models using Pydantic.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class FraudIndicatorResponse(BaseModel):
    """Fraud indicator in response."""
    type: str
    severity: str
    confidence: float
    description: str
    details: Dict[str, Any]


class AnalysisResultResponse(BaseModel):
    """Analysis result for a single land record."""
    land_id: str
    fraud_detected: bool
    risk_score: float = Field(..., ge=0, le=100)
    fraud_indicators: List[FraudIndicatorResponse]
    analysis_timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class BatchAnalysisResultResponse(BaseModel):
    """Batch analysis result."""
    total_records: int
    records_analyzed: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    results: List[AnalysisResultResponse]
    processing_time_seconds: float
    batch_id: str


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
    checks: Dict[str, bool]


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class UserInfoResponse(BaseModel):
    """User information response."""
    user_id: str
    role: str
    permissions: List[str]


class RateLimitInfoResponse(BaseModel):
    """Rate limit information response."""
    limit: int
    remaining: int
    reset_in_seconds: int
    window_seconds: int


class UploadResponse(BaseModel):
    """File upload response."""
    file_id: str
    filename: str
    size_bytes: int
    status: str
    message: Optional[str] = None
    analysis_job_id: Optional[str] = None