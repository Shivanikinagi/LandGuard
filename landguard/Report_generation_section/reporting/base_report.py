"""
LandGuard Phase 4: Base Report Class
Foundation for all report types
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum
from abc import ABC, abstractmethod
import logging


logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Types of reports"""
    FRAUD_ANALYSIS = "fraud_analysis"
    EXECUTIVE_SUMMARY = "executive_summary"
    DETAILED_ANALYSIS = "detailed_analysis"
    BATCH_ANALYSIS = "batch_analysis"
    DASHBOARD = "dashboard"


class ReportFormat(Enum):
    """Report output formats"""
    HTML = "html"
    PDF = "pdf"
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"


class RiskLevel(Enum):
    """Risk level classification"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class BaseReport(ABC):
    """
    Base class for all reports
    Provides common functionality and structure
    """
    
    def __init__(
        self,
        report_type: ReportType,
        title: str,
        description: Optional[str] = None
    ):
        self.report_type = report_type
        self.title = title
        self.description = description
        self.report_id = self._generate_report_id()
        self.created_at = datetime.now(timezone.utc)
        self.metadata: Dict[str, Any] = {}
        self.data: Dict[str, Any] = {}
        self.findings: List[Dict[str, Any]] = []
        self.recommendations: List[str] = []
        self.risk_level: Optional[RiskLevel] = None
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"RPT-{timestamp}-{hash(self.title) % 10000:04d}"
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to report"""
        self.metadata[key] = value
    
    def add_data(self, key: str, value: Any) -> None:
        """Add data to report"""
        self.data[key] = value
    
    def add_finding(
        self,
        title: str,
        description: str,
        severity: str,
        evidence: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a finding to the report"""
        finding = {
            'title': title,
            'description': description,
            'severity': severity,
            'evidence': evidence or {},
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self.findings.append(finding)
    
    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation"""
        self.recommendations.append(recommendation)
    
    def set_risk_level(self, risk_level: RiskLevel) -> None:
        """Set overall risk level"""
        self.risk_level = risk_level
    
    def get_summary(self) -> Dict[str, Any]:
        """Get report summary"""
        return {
            'report_id': self.report_id,
            'type': self.report_type.value,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'risk_level': self.risk_level.value if self.risk_level else None,
            'findings_count': len(self.findings),
            'recommendations_count': len(self.recommendations)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            'report_id': self.report_id,
            'type': self.report_type.value,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata,
            'data': self.data,
            'findings': self.findings,
            'recommendations': self.recommendations,
            'risk_level': self.risk_level.value if self.risk_level else None
        }
    
    @abstractmethod
    def generate(self, format: ReportFormat) -> bytes:
        """
        Generate report in specified format
        Must be implemented by subclasses
        """
        pass
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.report_id}, type={self.report_type.value})>"


class FraudAnalysisReport(BaseReport):
    """Report for fraud analysis results"""
    
    def __init__(
        self,
        property_id: str,
        analysis_results: Dict[str, Any]
    ):
        super().__init__(
            report_type=ReportType.FRAUD_ANALYSIS,
            title=f"Fraud Analysis Report - Property {property_id}",
            description="Detailed fraud detection analysis for land property"
        )
        
        self.property_id = property_id
        self.analysis_results = analysis_results
        
        # Add basic metadata
        self.add_metadata('property_id', property_id)
        self.add_metadata('analysis_timestamp', datetime.now(timezone.utc).isoformat())
        
        # Process analysis results
        self._process_results()
    
    def _process_results(self) -> None:
        """Process analysis results into report format"""
        results = self.analysis_results
        
        # Add property data
        if 'property' in results:
            self.add_data('property', results['property'])
        
        # Add fraud flags
        if 'fraud_flags' in results:
            flags = results['fraud_flags']
            self.add_data('fraud_flags', flags)
            
            # Convert flags to findings
            for flag in flags:
                self.add_finding(
                    title=flag.get('type', 'Unknown Fraud Type'),
                    description=flag.get('description', ''),
                    severity=flag.get('severity', 'medium'),
                    evidence=flag.get('evidence', {})
                )
        
        # Determine risk level
        risk_score = results.get('risk_score', 0)
        if risk_score >= 80:
            self.set_risk_level(RiskLevel.CRITICAL)
        elif risk_score >= 60:
            self.set_risk_level(RiskLevel.HIGH)
        elif risk_score >= 40:
            self.set_risk_level(RiskLevel.MEDIUM)
        elif risk_score > 0:
            self.set_risk_level(RiskLevel.LOW)
        else:
            self.set_risk_level(RiskLevel.NONE)
        
        # Add recommendations
        if 'recommendations' in results:
            for rec in results['recommendations']:
                self.add_recommendation(rec)
    
    def generate(self, format: ReportFormat) -> bytes:
        """Generate fraud analysis report"""
        # This will be implemented by exporters
        from .report_generator import ReportGenerator
        generator = ReportGenerator()
        return generator.export(self, format)


class ExecutiveSummaryReport(BaseReport):
    """Executive summary report for batch analysis"""
    
    def __init__(
        self,
        total_properties: int,
        fraud_detected: int,
        high_risk_properties: List[str]
    ):
        super().__init__(
            report_type=ReportType.EXECUTIVE_SUMMARY,
            title="Executive Summary - Fraud Detection Analysis",
            description="High-level overview of fraud detection results"
        )
        
        self.add_data('total_properties', total_properties)
        self.add_data('fraud_detected', fraud_detected)
        self.add_data('high_risk_properties', high_risk_properties)
        self.add_data('fraud_rate', (fraud_detected / total_properties * 100) if total_properties > 0 else 0)
    
    def generate(self, format: ReportFormat) -> bytes:
        """Generate executive summary"""
        from .report_generator import ReportGenerator
        generator = ReportGenerator()
        return generator.export(self, format)


# Export all classes
__all__ = [
    'BaseReport',
    'ReportType',
    'ReportFormat',
    'RiskLevel',
    'FraudAnalysisReport',
    'ExecutiveSummaryReport'
]