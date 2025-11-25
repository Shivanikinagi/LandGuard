"""
Data models for LandGuard fraud detection system.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class OwnerHistory(BaseModel):
    """Represents a single ownership record."""
    owner_name: str
    date: Optional[datetime] = None
    document_id: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('date', pre=True)
    def parse_date(cls, v):
        if isinstance(v, str):
            # Try multiple date formats
            from dateutil import parser
            try:
                return parser.parse(v)
            except:
                return None
        return v


class Transaction(BaseModel):
    """Represents a financial transaction related to the land."""
    tx_id: str
    date: Optional[datetime] = None
    amount: Optional[float] = None
    from_party: Optional[str] = None
    to_party: Optional[str] = None
    transaction_type: Optional[str] = None
    
    @validator('date', pre=True)
    def parse_date(cls, v):
        if isinstance(v, str):
            from dateutil import parser
            try:
                return parser.parse(v)
            except:
                return None
        return v


class LandRecord(BaseModel):
    """Complete land record with all metadata."""
    land_id: str
    owner_history: Optional[List[OwnerHistory]] = []
    transactions: Optional[List[Transaction]] = []
    property_area: Optional[float] = None
    registration_number: Optional[str] = None
    registration_date: Optional[datetime] = None
    location: Optional[str] = None
    property_type: Optional[str] = None
    raw_text: Optional[str] = None
    source_file: Optional[str] = None
    extraction_confidence: float = 1.0
    metadata: Optional[Dict[str, Any]] = {}
    
    @validator('registration_date', pre=True)
    def parse_date(cls, v):
        if isinstance(v, str):
            from dateutil import parser
            try:
                return parser.parse(v)
            except:
                return None
        return v


class Issue(BaseModel):
    """Represents a single detected anomaly or fraud indicator."""
    type: str  # e.g., "rapid_transfer", "party_mismatch", etc.
    message: str
    severity: str  # "low", "medium", "high"
    evidence: List[str]
    field: Optional[str] = None
    transaction_id: Optional[str] = None
    date_range: Optional[tuple] = None
    amount: Optional[float] = None
    
    class Config:
        json_encoders = {
            tuple: lambda v: list(v) if v else None
        }


class AnomalyReport(BaseModel):
    """Complete fraud detection report for a land record."""
    record_id: str
    source_file: str
    issues: List[Issue]
    confidence: float = Field(ge=0.0, le=1.0)
    generated_at: str
    total_issues: int
    highest_severity: str
    extracted_summary: Dict[str, Any]
    
    def dict(self, **kwargs):
        """Override dict to handle datetime serialization."""
        d = super().dict(**kwargs)
        # Ensure all datetime objects are converted to strings
        return d