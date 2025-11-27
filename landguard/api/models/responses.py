"""
API Response Models
Pydantic models for API responses
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime


class UserResponse(BaseModel):
    """User response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class LandRecordResponse(BaseModel):
    """Land record response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    record_number: str
    owner_name: str
    location: str
    area: float
    status: str
    document_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class AnalysisResponse(BaseModel):
    """Analysis response model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    land_record_id: int
    risk_level: str
    fraud_probability: float
    flags: List[str] = []
    recommendation: Optional[str] = None
    analyzed_by: Optional[str] = None
    created_at: datetime
    land_record: Optional[LandRecordResponse] = None


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response"""
    total_records: int
    flagged_records: int
    high_risk: int
    medium_risk: int
    low_risk: int
    fraud_percentage: float


class RecentAnalysisItem(BaseModel):
    """Recent analysis item"""
    id: int
    land_record_id: str
    risk_level: str
    fraud_probability: float
    created_at: str
    location: str


class FraudTrendItem(BaseModel):
    """Fraud trend item"""
    month: str
    count: int


class RiskDistributionItem(BaseModel):
    """Risk distribution item"""
    name: str
    value: int
    color: str


class DashboardResponse(BaseModel):
    """Dashboard response with all data"""
    statistics: DashboardStatsResponse
    recent_analyses: List[RecentAnalysisItem]
    fraud_trends: List[FraudTrendItem]
    risk_distribution: List[RiskDistributionItem]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: Optional[str] = None
    version: Optional[str] = None
    database: Optional[str] = None
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    error: Optional[str] = None


class SuccessResponse(BaseModel):
    """Generic success response"""
    message: str
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    """Paginated response model"""
    data: List[Any]
    total: int
    page: int
    limit: int
    total_pages: int


class UploadResponse(BaseModel):
    """File upload response"""
    filename: str
    size: int
    path: str
    message: str


class AnalysisDetailResponse(BaseModel):
    """Detailed analysis response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    land_record: LandRecordResponse
    risk_level: str
    fraud_probability: float
    flags: List[str]
    recommendation: Optional[str]
    analyzed_by: Optional[str]
    created_at: datetime
    details: Optional[Dict[str, Any]] = None


class StatisticsResponse(BaseModel):
    """Statistics response"""
    total_records: int
    analyzed_records: int
    pending_records: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    average_fraud_probability: float
    recent_activity: List[Dict[str, Any]]


class BatchUploadResponse(BaseModel):
    """Batch upload response"""
    total_files: int
    successful: int
    failed: int
    files: List[Dict[str, Any]]
    message: str