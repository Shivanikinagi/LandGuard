"""
Performance tests for LandGuard extractors and analyzers.
Tests execution time and throughput.
"""

import pytest
import time
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import List
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
from detector.extractors.json_extractor import JSONExtractor
from detector.extractors.csv_extractor import CSVExtractor
from core.analyzer import LandGuardAnalyzer
from core.models import LandRecord, OwnerHistory, Transaction


@pytest.mark.performance
class TestExtractorPerformance:
    """Performance tests for data extractors."""
    
    def test_json_extractor_single_record_performance(self, tmp_path, benchmark_timer):
        """Test JSON extraction performance for single record."""
        # Create test data
        data = {
            "land_id": "PERF-001",
            "owner_history": [
                {"owner_name": f"Owner {i}", "date": f"2020-{i%12+1:02d}-01"}
                for i in range(10)
            ],
            "transactions": [
                {
                    "tx_id": f"TX-{i}",
                    "amount": 1000000 * i,
                    "from_party": f"Party {i}",
                    "to_party": f"Party {i+1}"
                }
                for i in range(5)
            ],
            "property_area": 2500.5
        }
        
        test_file = tmp_path / "perf_test.json"
        with open(test_file, 'w') as f:
            json.dump(data, f)
        
        extractor = JSONExtractor()
        
        # Warmup
        extractor.extract(str(test_file))
        
        # Benchmark
        start_time = time.time()
        result = extractor.extract(str(test_file))
        elapsed_time = time.time() - start_time
        
        assert result['land_id'] == "PERF-001"
        assert elapsed_time < 0.1  # Should complete in under 100ms
        
        benchmark_timer.record("json_single_record", elapsed_time)
    
    def test_json_extractor_large_owner_history(self, tmp_path, benchmark_timer):
        """Test JSON extraction with large owner history."""
        # Create record with 1000 owners
        data = {
            "land_id": "PERF-002",
            "owner_history": [
                {
                    "owner_name": f"Owner {i}",
                    "date": f"2020-{(i%12)+1:02d}-{(i%28)+1:02d}",
                    "document_id": f"DOC-{i:06d}"
                }
                for i in range(1000)
            ]
        }
        
        test_file = tmp_path / "large_history.json"
        with open(test_file, 'w') as f:
            json.dump(data, f)
        
        extractor = JSONExtractor()
        
        start_time = time.time()
        result = extractor.extract(str(test_file))
        elapsed_time = time.time() - start_time
        
        assert len(result['owner_history']) == 1000
        assert elapsed_time < 1.0  # Should complete in under 1 second
        
        benchmark_timer.record("json_large_history", elapsed_time)
    
    def test_csv_extractor_performance(self, tmp_path, benchmark_timer):
        """Test CSV extraction performance."""
        test_file = tmp_path / "perf_test.csv"
        
        # Create CSV with 100 rows
        with open(test_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'land_id', 'owner_name', 'owner_date', 
                'tx_id', 'amount', 'property_area'
            ])
            writer.writeheader()
            
            for i in range(100):
                writer.writerow({
                    'land_id': 'LD-PERF',
                    'owner_name': f'Owner {i}',
                    'owner_date': f'2024-01-{(i%28)+1:02d}',
                    'tx_id': f'TX-{i}',
                    'amount': str(1000000 * i),
                    'property_area': '2500.5'
                })
        
        extractor = CSVExtractor()
        
        start_time = time.time()
        result = extractor.extract(str(test_file))
        elapsed_time = time.time() - start_time
        
        assert result['land_id'] == 'LD-PERF'
        assert len(result['owner_history']) >= 100
        assert elapsed_time < 0.5  # Should complete in under 500ms
        
        benchmark_timer.record("csv_100_rows", elapsed_time)
    
    def test_batch_extraction_performance(self, tmp_path, benchmark_timer):
        """Test batch extraction of multiple files."""
        # Create 50 JSON files
        for i in range(50):
            data = {
                "land_id": f"BATCH-{i:03d}",
                "owner_history": [{"owner_name": f"Owner {i}"}],
                "property_area": 1000.0 + i
            }
            
            file_path = tmp_path / f"record_{i:03d}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f)
        
        extractor = JSONExtractor()
        
        start_time = time.time()
        results = []
        for file_path in sorted(tmp_path.glob("record_*.json")):
            result = extractor.extract(str(file_path))
            results.append(result)
        elapsed_time = time.time() - start_time
        
        assert len(results) == 50
        assert elapsed_time < 2.0  # Should complete in under 2 seconds
        
        avg_time = elapsed_time / 50
        benchmark_timer.record("batch_50_files", elapsed_time)
        benchmark_timer.record("avg_per_file", avg_time)


@pytest.mark.performance
class TestAnalyzerPerformance:
    """Performance tests for fraud analyzer."""
    
    def test_analyze_simple_record_performance(self, benchmark_timer):
        """Test analysis performance for simple record."""
        record = LandRecord(
            land_id="PERF-ANALYZE-001",
            owner_history=[
                OwnerHistory(owner_name="Alice", date=datetime(2023, 1, 1))
            ],
            transactions=[
                Transaction(
                    tx_id="TX-001",
                    date=datetime(2023, 6, 1),
                    amount=5000000,
                    from_party="Alice",
                    to_party="Bob"
                )
            ]
        )
        
        analyzer = LandGuardAnalyzer()
        
        # Warmup
        analyzer.analyze_record(record)
        
        # Benchmark
        start_time = time.time()
        report = analyzer.analyze_record(record)
        elapsed_time = time.time() - start_time
        
        assert report.record_id == "PERF-ANALYZE-001"
        assert elapsed_time < 0.05  # Should complete in under 50ms
        
        benchmark_timer.record("analyze_simple", elapsed_time)
    
    def test_analyze_complex_record_performance(self, benchmark_timer):
        """Test analysis performance for complex record."""
        base_date = datetime(2020, 1, 1)
        
        # Create record with 50 owners and 100 transactions
        record = LandRecord(
            land_id="PERF-ANALYZE-002",
            owner_history=[
                OwnerHistory(
                    owner_name=f"Owner {i}",
                    date=base_date + timedelta(days=i*30)
                )
                for i in range(50)
            ],
            transactions=[
                Transaction(
                    tx_id=f"TX-{i:03d}",
                    date=base_date + timedelta(days=i*15),
                    amount=1000000 * (i + 1),
                    from_party=f"Owner {i}",
                    to_party=f"Owner {i+1}"
                )
                for i in range(100)
            ]
        )
        
        analyzer = LandGuardAnalyzer()
        
        start_time = time.time()
        report = analyzer.analyze_record(record)
        elapsed_time = time.time() - start_time
        
        assert report.record_id == "PERF-ANALYZE-002"
        assert elapsed_time < 0.5  # Should complete in under 500ms
        
        benchmark_timer.record("analyze_complex", elapsed_time)
    
    def test_batch_analyze_performance(self, benchmark_timer):
        """Test batch analysis performance."""
        # Create 100 records
        records = []
        for i in range(100):
            record = LandRecord(
                land_id=f"BATCH-{i:03d}",
                owner_history=[
                    OwnerHistory(
                        owner_name=f"Owner {j}",
                        date=datetime(2020 + j, 1, 1)
                    )
                    for j in range(5)
                ],
                transactions=[
                    Transaction(
                        tx_id=f"TX-{i}-{j}",
                        amount=1000000,
                        from_party=f"Owner {j}",
                        to_party=f"Owner {j+1}"
                    )
                    for j in range(3)
                ]
            )
            records.append(record)
        
        analyzer = LandGuardAnalyzer()
        
        start_time = time.time()
        reports = analyzer.batch_analyze(records)
        elapsed_time = time.time() - start_time
        
        assert len(reports) == 100
        assert elapsed_time < 10.0  # Should complete in under 10 seconds
        
        avg_time = elapsed_time / 100
        benchmark_timer.record("batch_analyze_100", elapsed_time)
        benchmark_timer.record("avg_analyze_per_record", avg_time)


@pytest.mark.performance
class TestThroughput:
    """Throughput tests - records per second."""
    
    def test_extraction_throughput(self, tmp_path, benchmark_timer):
        """Measure extraction throughput."""
        # Create 200 small JSON files
        for i in range(200):
            data = {
                "land_id": f"THROUGHPUT-{i:03d}",
                "owner_history": [{"owner_name": "Test"}],
                "property_area": 1000.0
            }
            
            file_path = tmp_path / f"t_{i:03d}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f)
        
        extractor = JSONExtractor()
        
        start_time = time.time()
        count = 0
        for file_path in sorted(tmp_path.glob("t_*.json")):
            extractor.extract(str(file_path))
            count += 1
        elapsed_time = time.time() - start_time
        
        throughput = count / elapsed_time
        
        assert throughput > 50  # At least 50 records/second
        
        benchmark_timer.record("extraction_throughput_rps", throughput)
        print(f"\n📊 Extraction Throughput: {throughput:.2f} records/second")
    
    def test_analysis_throughput(self, benchmark_timer):
        """Measure analysis throughput."""
        # Create 300 records
        records = [
            LandRecord(
                land_id=f"T-{i:03d}",
                owner_history=[
                    OwnerHistory(owner_name=f"Owner {j}")
                    for j in range(3)
                ]
            )
            for i in range(300)
        ]
        
        analyzer = LandGuardAnalyzer()
        
        start_time = time.time()
        for record in records:
            analyzer.analyze_record(record)
        elapsed_time = time.time() - start_time
        
        throughput = len(records) / elapsed_time
        
        assert throughput > 100  # At least 100 records/second
        
        benchmark_timer.record("analysis_throughput_rps", throughput)
        print(f"\n📊 Analysis Throughput: {throughput:.2f} records/second")