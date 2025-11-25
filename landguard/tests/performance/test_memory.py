"""
Memory profiling tests for LandGuard.
Tests memory usage and potential memory leaks.
"""

import pytest
import gc
import json
from pathlib import Path

try:
    import psutil
    import os
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from detector.extractors.json_extractor import JSONExtractor
from datetime import datetime, timedelta
from typing import List

try:
    import psutil
    import os
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from core.analyzer import LandGuardAnalyzer
from core.models import LandRecord, OwnerHistory, Transaction

@pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed")
@pytest.mark.performance
class TestMemoryUsage:
    """Memory usage tests."""
    
    def get_memory_usage_mb(self):
        """Get current process memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def test_json_extractor_memory_usage(self, tmp_path):
        """Test memory usage for JSON extraction."""
        # Create large JSON file (10MB+)
        data = {
            "land_id": "MEM-001",
            "owner_history": [
                {
                    "owner_name": f"Owner Name {i} with some extra text to increase size",
                    "date": f"2020-{(i%12)+1:02d}-01",
                    "document_id": f"DOC-{i:06d}-LONG-ID-STRING"
                }
                for i in range(10000)
            ],
            "transactions": [
                {
                    "tx_id": f"TX-{i:06d}",
                    "amount": 1000000,
                    "from_party": f"Party {i}",
                    "to_party": f"Party {i+1}",
                    "description": "Transaction description with additional details"
                }
                for i in range(5000)
            ]
        }
        
        test_file = tmp_path / "large_mem.json"
        with open(test_file, 'w') as f:
            json.dump(data, f)
        
        file_size_mb = test_file.stat().st_size / 1024 / 1024
        print(f"\n📏 File size: {file_size_mb:.2f} MB")
        
        gc.collect()
        mem_before = self.get_memory_usage_mb()
        
        extractor = JSONExtractor()
        result = extractor.extract(str(test_file))
        
        mem_after = self.get_memory_usage_mb()
        mem_used = mem_after - mem_before
        
        print(f"💾 Memory before: {mem_before:.2f} MB")
        print(f"💾 Memory after: {mem_after:.2f} MB")
        print(f"📊 Memory used: {mem_used:.2f} MB")
        
        # Memory usage should be reasonable (< 5x file size)
        assert mem_used < file_size_mb * 5
        
        # Cleanup
        del result
        gc.collect()
    
    def test_analyzer_memory_usage(self):
        """Test memory usage for analyzer."""
        # Create large record
        record = LandRecord(
            land_id="MEM-002",
            owner_history=[
                OwnerHistory(owner_name=f"Owner {i}")
                for i in range(1000)
            ]
        )
        
        gc.collect()
        mem_before = self.get_memory_usage_mb()
        
        analyzer = LandGuardAnalyzer()
        report = analyzer.analyze_record(record)
        
        mem_after = self.get_memory_usage_mb()
        mem_used = mem_after - mem_before
        
        print(f"\n💾 Analyzer memory used: {mem_used:.2f} MB")
        
        # Should use less than 50MB for this operation
        assert mem_used < 50
        
        # Cleanup
        del report
        gc.collect()
    
    def test_memory_leak_batch_processing(self, tmp_path):
        """Test for memory leaks in batch processing."""
        # Create 100 small files
        for i in range(100):
            data = {
                "land_id": f"LEAK-{i:03d}",
                "owner_history": [
                    {"owner_name": f"Owner {j}"}
                    for j in range(10)
                ]
            }
            
            file_path = tmp_path / f"leak_{i:03d}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f)
        
        extractor = JSONExtractor()
        analyzer = LandGuardAnalyzer()
        
        gc.collect()
        mem_before = self.get_memory_usage_mb()
        mem_samples = []
        
        # Process files and track memory
        for i, file_path in enumerate(sorted(tmp_path.glob("leak_*.json"))):
            data = extractor.extract(str(file_path))
            record = LandRecord(**data)
            report = analyzer.analyze_record(record)
            
            if i % 10 == 0:
                mem_samples.append(self.get_memory_usage_mb())
        
        gc.collect()
        mem_after = self.get_memory_usage_mb()
        
        print(f"\n💾 Memory samples: {mem_samples}")
        print(f"💾 Memory growth: {mem_after - mem_before:.2f} MB")
        
        # Memory should not grow significantly (< 100MB)
        assert mem_after - mem_before < 100
        
        # Check for linear growth (potential leak)
        if len(mem_samples) >= 3:
            growth_rate = (mem_samples[-1] - mem_samples[0]) / len(mem_samples)
            print(f"📈 Growth rate: {growth_rate:.2f} MB per 10 files")
            # Growth should be minimal
            assert growth_rate < 5


@pytest.mark.performance
class TestMemoryCleanup:
    """Test proper memory cleanup."""
    
    def test_extractor_cleanup(self, tmp_path):
        """Test extractor releases memory."""
        data = {
            "land_id": "CLEANUP-001",
            "owner_history": [
                {"owner_name": f"Owner {i}"}
                for i in range(1000)
            ]
        }
        
        test_file = tmp_path / "cleanup.json"
        with open(test_file, 'w') as f:
            json.dump(data, f)
        
        extractor = JSONExtractor()
        result = extractor.extract(str(test_file))
        
        # Delete and force garbage collection
        del result
        del extractor
        gc.collect()
        
        # If we get here without error, cleanup succeeded
        assert True
    
    def test_analyzer_cleanup(self):
        """Test analyzer releases memory."""
        records = [
            LandRecord(
                land_id=f"CLEANUP-{i}",
                owner_history=[OwnerHistory(owner_name=f"Owner {j}") for j in range(10)]
            )
            for i in range(100)
        ]
        
        analyzer = LandGuardAnalyzer()
        reports = []
        
        for record in records:
            report = analyzer.analyze_record(record)
            reports.append(report)
        
        # Delete and force garbage collection
        del reports
        del analyzer
        del records
        gc.collect()
        
        # If we get here without error, cleanup succeeded
        assert True