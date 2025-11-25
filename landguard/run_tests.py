"""
Test runner script for LandGuard.
Run with: python run_tests.py
"""

import sys
import pytest
from pathlib import Path

# Get the directory where this script is located (landguard/)
script_dir = Path(__file__).parent

# Add landguard to path
sys.path.insert(0, str(script_dir))

if __name__ == "__main__":
    # Change to the landguard directory before running tests
    import os
    os.chdir(script_dir)
    
    # Run pytest with coverage
    exit_code = pytest.main([
        "tests/",
        "-v",
        "--tb=short",
        "-ra",
        "-p", "no:pytest_ethereum",
        "-p", "no:web3"
    ])
    sys.exit(exit_code)