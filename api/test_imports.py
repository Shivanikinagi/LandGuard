#!/usr/bin/env python3
"""
Test script to verify imports work correctly
"""

import os
import sys

# Add parent directories to path to import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
pcc_path = os.path.join(project_root, 'pcc')
landguard_path = os.path.join(project_root, 'landguard')

sys.path.insert(0, project_root)
sys.path.insert(0, pcc_path)
sys.path.insert(0, landguard_path)

print("Testing imports...")

try:
    import flask
    print("✓ Flask imported successfully")
except ImportError as e:
    print("✗ Flask import failed:", e)

try:
    import flask_cors
    print("✓ Flask-CORS imported successfully")
except ImportError as e:
    print("✗ Flask-CORS import failed:", e)

try:
    from flask import Flask
    print("✓ Flask.Flask imported successfully")
except ImportError as e:
    print("✗ Flask.Flask import failed:", e)

try:
    from flask_cors import CORS
    print("✓ Flask-CORS.CORS imported successfully")
except ImportError as e:
    print("✗ Flask-CORS.CORS import failed:", e)

print("Import test completed.")