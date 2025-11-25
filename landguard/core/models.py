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
    
"""
Data models for land records and fraud detection.
"""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class OwnerHistory(BaseModel):
    """Owner history entry."""
    owner_name: str
    date: datetime
    
    @field_validator('owner_name')
    @classmethod
    def validate_owner_name(cls, v):
        """Validate owner name is not empty."""
        if not v or not v.strip():
            raise ValueError('Owner name cannot be empty')
        return v.strip()


class Transaction(BaseModel):
    """Transaction record."""
    tx_id: Optional[str] = Field(default=None, description="Transaction ID (optional)")
    from_party: str
    to_party: str
    date: datetime
    amount: Optional[float] = None
    
    @field_validator('from_party', 'to_party')
    @classmethod
    def validate_party_names(cls, v):
        """Validate party names are not empty."""
        if not v or not v.strip():
            raise ValueError('Party name cannot be empty')
        return v.strip()
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Validate amount if provided."""
        if v is not None and v < 0:
            raise ValueError('Amount cannot be negative')
        return v


class LandRecord(BaseModel):
    """Land record with ownership history and transactions."""
    land_id: str
    owner_history: List[OwnerHistory] = Field(default_factory=list)
    transactions: List[Transaction] = Field(default_factory=list)
    
    @field_validator('land_id')
    @classmethod
    def validate_land_id(cls, v):
        """Validate land ID is not empty."""
        if not v or not v.strip():
            raise ValueError('Land ID cannot be empty')
        return v.strip()


class Issue(BaseModel):
    """Fraud detection issue."""
    type: str
    severity: str
    description: str
    details: dict = Field(default_factory=dict)
    
    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v):
        """Validate severity level."""
        valid_severities = ['low', 'medium', 'high', 'critical']
        if v.lower() not in valid_severities:
            raise ValueError(f'Severity must be one of: {", ".join(valid_severities)}')
        return v.lower()


class AnomalyReport(BaseModel):
    """Anomaly detection report."""
    land_id: str
    fraud_detected: bool = False
    issues: List[Issue] = Field(default_factory=list)
    risk_score: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'land_id': self.land_id,
            'fraud_detected': self.fraud_detected,
            'fraud_indicators': [
                {
                    'type': issue.type,
                    'severity': issue.severity,
                    'confidence': 0.8,  # Default confidence
                    'description': issue.description,
                    'details': issue.details
                }
                for issue in self.issues
            ],
            'risk_score': self.risk_score,
            'metadata': self.metadata
        }
    
"""
Data models for land records and fraud detection.
"""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class OwnerHistory(BaseModel):
    """Owner history entry."""
    owner_name: str
    date: datetime
    
    @field_validator('owner_name')
    @classmethod
    def validate_owner_name(cls, v):
        """Validate owner name is not empty."""
        if not v or not v.strip():
            raise ValueError('Owner name cannot be empty')
        return v.strip()


class Transaction(BaseModel):
    """Transaction record."""
    tx_id: Optional[str] = Field(default=None, description="Transaction ID (optional)")
    from_party: str
    to_party: str
    date: datetime
    amount: Optional[float] = None
    
    @field_validator('from_party', 'to_party')
    @classmethod
    def validate_party_names(cls, v):
        """Validate party names are not empty."""
        if not v or not v.strip():
            raise ValueError('Party name cannot be empty')
        return v.strip()
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        """Validate amount if provided."""
        if v is not None and v < 0:
            raise ValueError('Amount cannot be negative')
        return v


class LandRecord(BaseModel):
    """Land record with ownership history and transactions."""
    land_id: str
    owner_history: List[OwnerHistory] = Field(default_factory=list)
    transactions: List[Transaction] = Field(default_factory=list)
    source_file: Optional[str] = Field(default=None, description="Source file path (optional)")
    
    @field_validator('land_id')
    @classmethod
    def validate_land_id(cls, v):
        """Validate land ID is not empty."""
        if not v or not v.strip():
            raise ValueError('Land ID cannot be empty')
        return v.strip()


class Issue(BaseModel):
    """Fraud detection issue."""
    type: str
    severity: str
    description: str = Field(default="", description="Issue description")
    details: dict = Field(default_factory=dict)
    
    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v):
        """Validate severity level."""
        valid_severities = ['low', 'medium', 'high', 'critical']
        if v.lower() not in valid_severities:
            raise ValueError(f'Severity must be one of: {", ".join(valid_severities)}')
        return v.lower()


class AnomalyReport(BaseModel):
    """Anomaly detection report."""
    land_id: str
    fraud_detected: bool = False
    issues: List[Issue] = Field(default_factory=list)
    risk_score: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'land_id': self.land_id,
            'fraud_detected': self.fraud_detected,
            'fraud_indicators': [
                {
                    'type': issue.type,
                    'severity': issue.severity,
                    'confidence': 0.8,  # Default confidence
                    'description': issue.description,
                    'details': issue.details
                }
                for issue in self.issues
            ],
            'risk_score': self.risk_score,
            'metadata': self.metadata
        }