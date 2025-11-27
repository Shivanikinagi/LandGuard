"""
API Models Package
"""

from .requests import (
    UserLoginRequest,
    UserCreateRequest,
    UserUpdateRequest,
    PasswordChangeRequest,
    LandRecordCreateRequest,
    LandRecordUpdateRequest,
    AnalysisCreateRequest,
    FileUploadRequest,
    BatchAnalysisRequest,
    SearchRequest,
    ReportGenerationRequest,
)

from .responses import (
    UserResponse,
    TokenResponse,
    LandRecordResponse,
    AnalysisResponse,
    DashboardStatsResponse,
    RecentAnalysisItem,
    FraudTrendItem,
    RiskDistributionItem,
    DashboardResponse,
    HealthResponse,
    ErrorResponse,
    SuccessResponse,
    PaginatedResponse,
    UploadResponse,
    AnalysisDetailResponse,
    StatisticsResponse,
    BatchUploadResponse,
)

__all__ = [
    # Requests
    'UserLoginRequest',
    'UserCreateRequest',
    'UserUpdateRequest',
    'PasswordChangeRequest',
    'LandRecordCreateRequest',
    'LandRecordUpdateRequest',
    'AnalysisCreateRequest',
    'FileUploadRequest',
    'BatchAnalysisRequest',
    'SearchRequest',
    'ReportGenerationRequest',
    # Responses
    'UserResponse',
    'TokenResponse',
    'LandRecordResponse',
    'AnalysisResponse',
    'DashboardStatsResponse',
    'RecentAnalysisItem',
    'FraudTrendItem',
    'RiskDistributionItem',
    'DashboardResponse',
    'HealthResponse',
    'ErrorResponse',
    'SuccessResponse',
    'PaginatedResponse',
    'UploadResponse',
    'AnalysisDetailResponse',
    'StatisticsResponse',
    'BatchUploadResponse',
]