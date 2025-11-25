"""
API request models using Pydantic.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


class OwnerHistoryRequest(BaseModel):
    """Owner history entry in request."""
    owner_name: str = Field(..., min_length=1, max_length=100)
    date: str = Field(..., description="Date in ISO format (YYYY-MM-DD)")
    
    @validator('date')
    def validate_date_format(cls, v):
        """Validate date is in ISO format."""
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("Date must be in ISO format (YYYY-MM-DD)")


class TransactionRequest(BaseModel):
    """Transaction entry in request."""
    from_party: str = Field(..., min_length=1, max_length=100)
    to_party: str = Field(..., min_length=1, max_length=100)
    date: str = Field(..., description="Date in ISO format (YYYY-MM-DD)")
    amount: Optional[float] = Field(None, ge=0, description="Transaction amount")
    
    @validator('date')
    def validate_date_format(cls, v):
        """Validate date is in ISO format."""
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("Date must be in ISO format (YYYY-MM-DD)")


class LandRecordRequest(BaseModel):
    """Land record for analysis request."""
    land_id: str = Field(..., min_length=1, max_length=50)
    owner_history: List[OwnerHistoryRequest] = Field(..., min_items=1)
    transactions: Optional[List[TransactionRequest]] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "land_id": "LAND-123-ABC",
                "owner_history": [
                    {
                        "owner_name": "John Doe",
                        "date": "2020-01-15"
                    },
                    {
                        "owner_name": "Jane Smith",
                        "date": "2023-06-20"
                    }
                ],
                "transactions": [
                    {
                        "from_party": "John Doe",
                        "to_party": "Jane Smith",
                        "date": "2023-06-20",
                        "amount": 500000
                    }
                ]
            }
        }


class BatchAnalysisRequest(BaseModel):
    """Batch analysis request."""
    records: List[LandRecordRequest] = Field(..., min_items=1, max_items=100)
    options: Optional[dict] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "records": [
                    {
                        "land_id": "LAND-001",
                        "owner_history": [
                            {"owner_name": "Alice", "date": "2020-01-01"},
                            {"owner_name": "Bob", "date": "2023-01-01"}
                        ]
                    }
                ],
                "options": {
                    "include_details": True
                }
            }
        }


class TokenRequest(BaseModel):
    """JWT token request."""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8)


class TokenRefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str = Field(...)