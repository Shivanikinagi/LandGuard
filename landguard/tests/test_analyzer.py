"""
Tests for LandGuard fraud detection analyzer.
"""

import pytest
from datetime import datetime, timedelta
from landguard.core.landguard.analyzer import LandGuardAnalyzer
from landguard.core.models import LandRecord, OwnerHistory, Transaction


class TestLandGuardAnalyzer:
    
    def test_missing_fields_detection(self):
        """Test detection of missing mandatory fields."""
        analyzer = LandGuardAnalyzer()
        
        # Record with missing land_id
        record = LandRecord(land_id="", owner_history=[])
        report = analyzer.analyze_record(record)
        
        assert report.total_issues > 0
        assert any(issue.type == "missing_field" for issue in report.issues)
    
    def test_rapid_transfer_detection(self):
        """Test detection of rapid ownership transfers."""
        analyzer = LandGuardAnalyzer()
        
        base_date = datetime(2024, 1, 1)
        record = LandRecord(
            land_id="LD-001",
            owner_history=[
                OwnerHistory(owner_name="Alice", date=base_date),
                OwnerHistory(owner_name="Bob", date=base_date + timedelta(days=30)),
                OwnerHistory(owner_name="Charlie", date=base_date + timedelta(days=60))
            ]
        )
        
        report = analyzer.analyze_record(record)
        
        assert any(issue.type == "rapid_transfer" for issue in report.issues)
        assert report.highest_severity == "high"
    
    def test_party_mismatch_detection(self):
        """Test detection of transaction party mismatches."""
        analyzer = LandGuardAnalyzer()
        
        base_date = datetime(2024, 1, 1)
        record = LandRecord(
            land_id="LD-002",
            owner_history=[
                OwnerHistory(owner_name="Alice", date=base_date)
            ],
            transactions=[
                Transaction(
                    tx_id="TX-001",
                    date=base_date + timedelta(days=10),
                    from_party="Bob",  # Mismatch!
                    to_party="Charlie",
                    amount=100000
                )
            ]
        )
        
        report = analyzer.analyze_record(record)
        
        assert any(issue.type == "party_mismatch" for issue in report.issues)
    
    def test_large_transfer_detection(self):
        """Test detection of large financial transfers."""
        analyzer = LandGuardAnalyzer()
        
        record = LandRecord(
            land_id="LD-003",
            owner_history=[
                OwnerHistory(owner_name="Alice", date=datetime(2024, 1, 1))
            ],
            transactions=[
                Transaction(
                    tx_id="TX-002",
                    date=datetime(2024, 1, 15),
                    from_party="Alice",
                    to_party="Bob",
                    amount=50000000  # 50M
                )
            ]
        )
        
        report = analyzer.analyze_record(record)
        
        assert any(issue.type == "large_transfer" for issue in report.issues)
    
    def test_duplicate_land_id_detection(self):
        """Test detection of duplicate land IDs."""
        analyzer = LandGuardAnalyzer()
        
        record1 = LandRecord(
            land_id="LD-004",
            owner_history=[OwnerHistory(owner_name="Alice", date=datetime(2024, 1, 1))],
            source_file="file1.json"
        )
        
        record2 = LandRecord(
            land_id="LD-004",  # Duplicate!
            owner_history=[OwnerHistory(owner_name="Bob", date=datetime(2024, 2, 1))],
            source_file="file2.json"
        )
        
        # Analyze first record
        analyzer.analyze_record(record1)
        
        # Analyze second record - should detect duplicate
        report2 = analyzer.analyze_record(record2)
        
        assert any(issue.type == "duplicate_land_id" for issue in report2.issues)
    
    def test_time_order_conflict(self):
        """Test detection of chronological issues in owner history."""
        analyzer = LandGuardAnalyzer()
        
        record = LandRecord(
            land_id="LD-005",
            owner_history=[
                OwnerHistory(owner_name="Alice", date=datetime(2024, 3, 1)),
                OwnerHistory(owner_name="Bob", date=datetime(2024, 1, 1))  # Earlier date!
            ]
        )
        
        report = analyzer.analyze_record(record)
        
        assert any(issue.type == "time_order_conflict" for issue in report.issues)
    
    def test_clean_record(self):
        """Test that clean record produces no issues."""
        analyzer = LandGuardAnalyzer()
        
        record = LandRecord(
            land_id="LD-006",
            owner_history=[
                OwnerHistory(owner_name="Alice", date=datetime(2023, 1, 1)),
                OwnerHistory(owner_name="Bob", date=datetime(2024, 1, 1))
            ],
            transactions=[
                Transaction(
                    tx_id="TX-003",
                    date=datetime(2024, 1, 5),
                    from_party="Alice",
                    to_party="Bob",
                    amount=500000
                )
            ],
            property_area=1000.0,
            registration_number="REG-123"
        )
        
        report = analyzer.analyze_record(record)
        
        assert report.total_issues == 0
        assert report.confidence == 1.0
        assert report.highest_severity == "none"
    
    def test_batch_analysis(self):
        """Test batch analysis of multiple records."""
        analyzer = LandGuardAnalyzer()
        
        records = [
            LandRecord(
                land_id="LD-007",
                owner_history=[OwnerHistory(owner_name="Alice", date=datetime(2024, 1, 1))],
                source_file="file1.json"
            ),
            LandRecord(
                land_id="LD-008",
                owner_history=[OwnerHistory(owner_name="Bob", date=datetime(2024, 1, 1))],
                source_file="file2.json"
            )
        ]
        
        reports = analyzer.batch_analyze(records)
        
        assert len(reports) == 2
        assert all(isinstance(r.confidence, float) for r in reports)