"""
API Request Models
Pydantic models for API requests
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserLoginRequest(BaseModel):
    """User login request"""
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    password: str = Field(..., min_length=6, description="Password")


class UserCreateRequest(BaseModel):
    """User creation request"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    role: str = Field(default="VIEWER")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        allowed_roles = ['ADMIN', 'ANALYST', 'VIEWER']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of {allowed_roles}')
        return v


class UserUpdateRequest(BaseModel):
    """User update request"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed_roles = ['ADMIN', 'ANALYST', 'VIEWER']
            if v not in allowed_roles:
                raise ValueError(f'Role must be one of {allowed_roles}')
        return v


class PasswordChangeRequest(BaseModel):
    """Password change request"""
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v


class LandRecordCreateRequest(BaseModel):
    """Land record creation request"""
    record_number: str = Field(..., min_length=1)
    owner_name: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    area: float = Field(..., gt=0, description="Area in square meters")
    status: str = Field(default="PENDING")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed_statuses = ['PENDING', 'ANALYZED', 'VERIFIED', 'FLAGGED']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of {allowed_statuses}')
        return v


class LandRecordUpdateRequest(BaseModel):
    """Land record update request"""
    owner_name: Optional[str] = None
    location: Optional[str] = None
    area: Optional[float] = Field(None, gt=0)
    status: Optional[str] = None
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed_statuses = ['PENDING', 'ANALYZED', 'VERIFIED', 'FLAGGED']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of {allowed_statuses}')
        return v


class AnalysisCreateRequest(BaseModel):
    """Analysis creation request"""
    land_record_id: int = Field(..., gt=0)
    risk_level: str
    fraud_probability: float = Field(..., ge=0, le=1)
    flags: List[str] = []
    recommendation: Optional[str] = None
    analyzed_by: Optional[str] = None
    
    @field_validator('risk_level')
    @classmethod
    def validate_risk_level(cls, v: str) -> str:
        allowed_levels = ['HIGH', 'MEDIUM', 'LOW']
        if v not in allowed_levels:
            raise ValueError(f'Risk level must be one of {allowed_levels}')
        return v


class FileUploadRequest(BaseModel):
    """File upload metadata request"""
    description: Optional[str] = Field(None, max_length=500)
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None


class BatchAnalysisRequest(BaseModel):
    """Batch analysis request"""
    land_record_ids: List[int] = Field(..., min_length=1, max_length=100)
    priority: str = Field(default="NORMAL")
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        allowed_priorities = ['HIGH', 'NORMAL', 'LOW']
        if v not in allowed_priorities:
            raise ValueError(f'Priority must be one of {allowed_priorities}')
        return v


class SearchRequest(BaseModel):
    """Search request"""
    query: str = Field(..., min_length=1, max_length=200)
    filters: Optional[Dict[str, Any]] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class ReportGenerationRequest(BaseModel):
    """Report generation request"""
    report_type: str = Field(..., description="Type of report: PDF, CSV, HTML")
    land_record_ids: Optional[List[int]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    include_analysis: bool = True
    
    @field_validator('report_type')
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        allowed_types = ['PDF', 'CSV', 'HTML', 'JSON']
        if v.upper() not in allowed_types:
            raise ValueError(f'Report type must be one of {allowed_types}')
        return v.upper()