"""
Entry point for LandGuard CLI.
Run from the compression- directory: python landguard/landguard_cli.py
"""

import sys
from pathlib import Path

# Add landguard to path
landguard_path = Path(__file__).parent
sys.path.insert(0, str(landguard_path))

from cli.main import app

if __name__ == "__main__":
    app()