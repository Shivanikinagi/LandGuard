"""
LandGuard - Land Registry Fraud Detection System
"""

__version__ = "0.1.0"

# Import from correct paths
from core.analyzer import LandGuardAnalyzer
from core.models import LandRecord, AnomalyReport, Issue, OwnerHistory, Transaction
from core.config import ConfigLoader, load_config, get_config

__all__ = [
    'LandGuardAnalyzer',
    'LandRecord',
    'AnomalyReport',
    'Issue',
    'OwnerHistory',
    'Transaction',
    'ConfigLoader',
    'load_config',
    'get_config',
]