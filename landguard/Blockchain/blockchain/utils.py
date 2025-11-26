"""
LandGuard Blockchain Utilities
Common helper functions for blockchain operations
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import yaml


def load_config(config_path: str = "blockchain_config.yaml") -> Dict[str, Any]:
    """Load blockchain configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def ensure_directory(directory: str) -> Path:
    """Create directory if it doesn't exist"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_storage_path(subdir: str) -> Path:
    """Get path to storage subdirectory"""
    base_path = Path("blockchain/storage")
    storage_path = base_path / subdir
    return ensure_directory(storage_path)


def generate_hash(data: bytes, algorithm: str = "sha256") -> str:
    """Generate hash of data using specified algorithm"""
    hasher = hashlib.new(algorithm)
    hasher.update(data)
    return hasher.hexdigest()


def generate_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """Generate hash of file contents"""
    hasher = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def save_json(data: Dict[str, Any], filepath: str) -> None:
    """Save data as JSON file"""
    ensure_directory(os.path.dirname(filepath))
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def load_json(filepath: str) -> Dict[str, Any]:
    """Load data from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def get_timestamp() -> str:
    """Get current ISO 8601 timestamp"""
    return datetime.utcnow().isoformat() + 'Z'


def format_bytes(size: int) -> str:
    """Format byte size as human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def validate_hash(hash_string: str, algorithm: str = "sha256") -> bool:
    """Validate hash string format"""
    expected_length = {
        "sha256": 64,
        "sha512": 128,
        "md5": 32
    }.get(algorithm, 64)
    
    if len(hash_string) != expected_length:
        return False
    
    try:
        int(hash_string, 16)
        return True
    except ValueError:
        return False


def get_file_metadata(file_path: str) -> Dict[str, Any]:
    """Get file metadata"""
    path = Path(file_path)
    stat = path.stat()
    
    return {
        "filename": path.name,
        "size_bytes": stat.st_size,
        "size_formatted": format_bytes(stat.st_size),
        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "extension": path.suffix,
        "absolute_path": str(path.absolute())
    }


def create_audit_entry(
    action: str,
    details: Dict[str, Any],
    user: Optional[str] = None
) -> Dict[str, Any]:
    """Create standardized audit log entry"""
    return {
        "timestamp": get_timestamp(),
        "action": action,
        "user": user or "system",
        "details": details,
        "hash": generate_hash(json.dumps(details, sort_keys=True).encode())
    }


def verify_ipfs_cid(cid: str) -> bool:
    """Basic validation of IPFS CID format"""
    # CIDv0: starts with Qm, 46 characters
    # CIDv1: starts with b, variable length
    if cid.startswith("Qm") and len(cid) == 46:
        return True
    if cid.startswith("b") and len(cid) > 20:
        return True
    return False


class BlockchainError(Exception):
    """Base exception for blockchain operations"""
    pass


class HashVerificationError(BlockchainError):
    """Hash verification failed"""
    pass


class IPFSError(BlockchainError):
    """IPFS operation failed"""
    pass


class SignatureError(BlockchainError):
    """Digital signature operation failed"""
    pass


# Export all utilities
__all__ = [
    'load_config',
    'ensure_directory',
    'get_storage_path',
    'generate_hash',
    'generate_file_hash',
    'save_json',
    'load_json',
    'get_timestamp',
    'format_bytes',
    'validate_hash',
    'get_file_metadata',
    'create_audit_entry',
    'verify_ipfs_cid',
    'BlockchainError',
    'HashVerificationError',
    'IPFSError',
    'SignatureError'
]