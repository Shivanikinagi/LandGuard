"""
Unit tests for LandGuard data models
Run with: pytest tests/test_models.py -v
"""

import pytest
from datetime import date, datetime
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import (
    Owner, Transaction, LandRecord, AnomalyIssue, AnomalyReport,
    Severity, IssueType, ExtractionResult
)


class TestOwner:
    """Test Owner model"""
    
    def test_create_owner(self):
        owner = Owner("Alice Kumar", date(2020, 1, 15), "DOC001")
        assert owner.name == "Alice Kumar"
        assert owner.date == date(2020, 1, 15)
        assert owner.document_id == "DOC001"
    
    def test_owner_serialization(self):
        owner = Owner("Bob Shah", date(2021, 6, 20))
        owner_dict = owner.to_dict()
        restored = Owner.from_dict(owner_dict)
        
        assert restored.name == owner.name
        assert restored.date == owner.date
    
    def test_owner_without_document(self):
        owner = Owner("Test User", date(2022, 3, 10))
        assert owner.document_id is None


class TestTransaction:
    """Test Transaction model"""
    
    def test_create_transaction(self):
        tx = Transaction(
            "TX001",
            date(2020, 5, 15),
            5000000,
            "Alice",
            "Bob",
            "DOC002"
        )
        assert tx.tx_id == "TX001"
        assert tx.amount == 5000000
        assert tx.from_party == "Alice"
        assert tx.to_party == "Bob"
    
    def test_transaction_serialization(self):
        tx = Transaction("TX002", date(2021, 7, 20), 7500000, "Bob", "Carol")
        tx_dict = tx.to_dict()
        restored = Transaction.from_dict(tx_dict)
        
        assert restored.tx_id == tx.tx_id
        assert restored.amount == tx.amount
        assert restored.from_party == tx.from_party
    
    def test_transaction_types(self):
        sale = Transaction("TX003", date(2022, 1, 1), 1000000, "A", "B", transaction_type="sale")
        gift = Transaction("TX004", date(2022, 2, 1), 0, "A", "B", transaction_type="gift")
        
        assert sale.transaction_type == "sale"
        assert gift.transaction_type == "gift"


class TestLandRecord:
    """Test LandRecord model"""
    
    @pytest.fixture
    def sample_record(self):
        owners = [
            Owner("Alice", date(2018, 1, 15)),
            Owner("Bob", date(2020, 6, 20)),
            Owner("Carol", date(2024, 3, 10))
        ]
        
        transactions = [
            Transaction("TX001", date(2020, 6, 20), 5000000, "Alice", "Bob"),
            Transaction("TX002", date(2024, 3, 10), 7500000, "Bob", "Carol")
        ]
        
        return LandRecord(
            land_id="LD-12345",
            owner_history=owners,
            transactions=transactions,
            area=2500.0,
            location="Mumbai"
        )
    
    def test_create_land_record(self, sample_record):
        assert sample_record.land_id == "LD-12345"
        assert len(sample_record.owner_history) == 3
        assert len(sample_record.transactions) == 2
        assert sample_record.area == 2500.0
    
    def test_get_current_owner(self, sample_record):
        current = sample_record.get_current_owner()
        assert current.name == "Carol"
        assert current.date == date(2024, 3, 10)
    
    def test_get_owner_at_date(self, sample_record):
        owner_2019 = sample_record.get_owner_at_date(date(2019, 1, 1))
        assert owner_2019.name == "Alice"
        
        owner_2022 = sample_record.get_owner_at_date(date(2022, 1, 1))
        assert owner_2022.name == "Bob"
    
    def test_land_record_serialization(self, sample_record):
        record_dict = sample_record.to_dict()
        restored = LandRecord.from_dict(record_dict)
        
        assert restored.land_id == sample_record.land_id
        assert len(restored.owner_history) == len(sample_record.owner_history)
        assert len(restored.transactions) == len(sample_record.transactions)
    
    def test_empty_owner_history(self):
        record = LandRecord(
            land_id="LD-99999",
            owner_history=[],
            transactions=[]
        )
        assert record.get_current_owner() is None


class TestAnomalyIssue:
    """Test AnomalyIssue model"""
    
    def test_create_issue(self):
        issue = AnomalyIssue(
            IssueType.RAPID_TRANSFER,
            Severity.HIGH,
            "Rapid transfer detected",
            ["Evidence 1", "Evidence 2"]
        )
        assert issue.issue_type == IssueType.RAPID_TRANSFER
        assert issue.severity == Severity.HIGH
        assert len(issue.evidence) == 2
    
    def test_issue_serialization(self):
        issue = AnomalyIssue(
            IssueType.PARTY_MISMATCH,
            Severity.CRITICAL,
            "Party mismatch detected"
        )
        issue_dict = issue.to_dict()
        restored = AnomalyIssue.from_dict(issue_dict)
        
        assert restored.issue_type == issue.issue_type
        assert restored.severity == issue.severity


class TestAnomalyReport:
    """Test AnomalyReport model"""
    
    @pytest.fixture
    def sample_issues(self):
        return [
            AnomalyIssue(IssueType.RAPID_TRANSFER, Severity.HIGH, "Issue 1"),
            AnomalyIssue(IssueType.LARGE_TRANSFER, Severity.MEDIUM, "Issue 2"),
            AnomalyIssue(IssueType.MISSING_FIELD, Severity.LOW, "Issue 3")
        ]
    
    def test_create_report(self, sample_issues):
        report = AnomalyReport(
            land_id="LD-12345",
            issues=sample_issues,
            confidence=0.85,
            generated_at=datetime.now()
        )
        
        assert report.land_id == "LD-12345"
        assert report.total_issues == 3
        assert report.highest_severity == Severity.HIGH
        assert 0 <= report.risk_score <= 1.0
    
    def test_empty_report(self):
        report = AnomalyReport(
            land_id="LD-00000",
            issues=[],
            confidence=1.0,
            generated_at=datetime.now()
        )
        
        assert report.total_issues == 0
        assert report.highest_severity is None
        assert report.risk_score == 0.0
    
    def test_has_high_risk_issues(self, sample_issues):
        report = AnomalyReport(
            land_id="LD-12345",
            issues=sample_issues,
            confidence=0.85,
            generated_at=datetime.now()
        )
        
        assert report.has_high_risk_issues() is True
    
    def test_get_issues_by_severity(self, sample_issues):
        report = AnomalyReport(
            land_id="LD-12345",
            issues=sample_issues,
            confidence=0.85,
            generated_at=datetime.now()
        )
        
        high_issues = report.get_issues_by_severity(Severity.HIGH)
        assert len(high_issues) == 1
        
        medium_issues = report.get_issues_by_severity(Severity.MEDIUM)
        assert len(medium_issues) == 1
    
    def test_report_summary(self, sample_issues):
        report = AnomalyReport(
            land_id="LD-12345",
            issues=sample_issues,
            confidence=0.85,
            generated_at=datetime.now()
        )
        
        summary = report.summary()
        assert "3 issue(s) detected" in summary
        assert "HIGH" in summary
    
    def test_report_serialization(self, sample_issues):
        report = AnomalyReport(
            land_id="LD-12345",
            issues=sample_issues,
            confidence=0.85,
            generated_at=datetime.now()
        )
        
        report_dict = report.to_dict()
        restored = AnomalyReport.from_dict(report_dict)
        
        assert restored.land_id == report.land_id
        assert len(restored.issues) == len(report.issues)
        assert restored.confidence == report.confidence


class TestExtractionResult:
    """Test ExtractionResult model"""
    
    def test_successful_extraction(self):
        record = LandRecord(
            land_id="LD-12345",
            owner_history=[],
            transactions=[]
        )
        
        result = ExtractionResult(
            success=True,
            record=record,
            extraction_method="pdf"
        )
        
        assert result.success is True
        assert result.record is not None
        assert result.error is None
    
    def test_failed_extraction(self):
        result = ExtractionResult(
            success=False,
            error="Failed to parse PDF"
        )
        
        assert result.success is False
        assert result.record is None
        assert result.error == "Failed to parse PDF"
    
    def test_extraction_with_warnings(self):
        record = LandRecord(
            land_id="LD-12345",
            owner_history=[],
            transactions=[]
        )
        
        result = ExtractionResult(
            success=True,
            record=record,
            warnings=["Low OCR confidence", "Missing area field"],
            extraction_method="ocr"
        )
        
        assert len(result.warnings) == 2
        assert result.extraction_method == "ocr"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])