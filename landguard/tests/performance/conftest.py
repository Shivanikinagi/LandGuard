"""
Pytest configuration and fixtures for performance tests.
"""

import pytest
import time
from typing import Dict, List


class BenchmarkTimer:
    """Helper class to record and display benchmark results."""
    
    def __init__(self):
        self.results: Dict[str, float] = {}
    
    def record(self, name: str, value: float):
        """Record a benchmark result."""
        self.results[name] = value
    
    def get_results(self) -> Dict[str, float]:
        """Get all recorded results."""
        return self.results.copy()
    
    def print_summary(self):
        """Print benchmark summary."""
        if not self.results:
            return
        
        print("\n" + "="*60)
        print("📊 BENCHMARK SUMMARY")
        print("="*60)
        
        for name, value in sorted(self.results.items()):
            if 'throughput' in name or 'rps' in name:
                print(f"  {name:40s}: {value:8.2f} records/sec")
            elif 'ms' in name:
                print(f"  {name:40s}: {value:8.2f} ms")
            elif '_s' in name:
                print(f"  {name:40s}: {value:8.4f} s")
            else:
                print(f"  {name:40s}: {value:8.4f}")
        
        print("="*60 + "\n")


@pytest.fixture
def benchmark_timer():
    """Provide a benchmark timer for tests."""
    timer = BenchmarkTimer()
    yield timer
    timer.print_summary()


@pytest.fixture(scope="session")
def performance_config():
    """Provide performance test configuration."""
    return {
        'max_extraction_time_ms': 100,
        'max_analysis_time_ms': 50,
        'min_throughput_rps': 50,
        'max_memory_usage_mb': 500,
        'batch_size': 100
    }


@pytest.fixture
def timer():
    """Simple timer fixture for measuring execution time."""
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        def elapsed(self) -> float:
            if self.start_time is None or self.end_time is None:
                return 0.0
            return self.end_time - self.start_time
        
        def elapsed_ms(self) -> float:
            return self.elapsed() * 1000
    
    return Timer()


def pytest_configure(config):
    """Register custom markers for performance tests."""
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "benchmark: mark test as a detailed benchmark"
    )
    config.addinivalue_line(
        "markers", "memory: mark test as a memory profiling test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark slow tests."""
    for item in items:
        if "performance" in item.nodeid:
            if "benchmark" in item.nodeid or "memory" in item.nodeid:
                item.add_marker(pytest.mark.slow)