"""
Performance test runner for LandGuard.
Run with: python run_performance_tests.py
"""

import sys
import os
import pytest
from pathlib import Path

# Get the directory where this script is located (landguard/)
script_dir = Path(__file__).parent

# Add landguard to path
sys.path.insert(0, str(script_dir))

if __name__ == "__main__":
    # Change to the landguard directory before running tests
    os.chdir(script_dir)
    
    print("🚀 Running LandGuard Performance Tests\n")
    print("=" * 60)
    print(f"Working directory: {os.getcwd()}")
    print(f"Looking for tests in: {script_dir / 'tests' / 'performance'}")
    print("=" * 60 + "\n")
    
    # Check if performance tests directory exists
    perf_test_dir = script_dir / "tests" / "performance"
    if not perf_test_dir.exists():
        print(f"❌ ERROR: Performance tests directory not found!")
        print(f"Expected location: {perf_test_dir}")
        print(f"\nPlease ensure the following directories exist:")
        print(f"  - {script_dir / 'tests' / 'performance'}")
        print(f"  - {script_dir / 'tests' / 'fixtures'}")
        sys.exit(1)
    
    # Run performance tests
    exit_code = pytest.main([
        "tests/performance/",
        "-v",
        "--tb=short",
        "-ra",
        "-p", "no:pytest_ethereum",
        "-p", "no:web3",
        "-m", "performance"
    ])
    
    sys.exit(exit_code)