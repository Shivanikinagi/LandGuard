"""
Encryption utilities for sensitive data.
Provides symmetric encryption, hashing, and key management.
"""

import os
import base64
import hashlib
from typing import Optional, Union
from pathlib import Path

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


class DataEncryptor:
    """Encrypt and decrypt sensitive data."""
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize encryptor with encryption key.
        
        Args:
            key: Encryption key (32 bytes, base64 encoded)
                 If None, will try to load from environment or generate new
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError(
                "cryptography library not installed. "
                "Install with: pip install cryptography"
            )
        
        if key is None:
            key = self._load_or_generate_key()
        
        self.fernet = Fernet(key)
        self._key = key
    
    def _load_or_generate_key(self) -> bytes:
        """Load encryption key from environment or generate new one."""
        # Try to load from environment
        key_env = os.getenv('LANDGUARD_ENCRYPTION_KEY')
        if key_env:
            return key_env.encode()
        
        # Generate new key
        return Fernet.generate_key()
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt (string or bytes)
            
        Returns:
            Base64-encoded encrypted data as string
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted = self.fernet.encrypt(data)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            
        Returns:
            Decrypted data as string
        """
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        decrypted = self.fernet.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
    
    def encrypt_file(self, input_path: Path, output_path: Path):
        """
        Encrypt a file.
        
        Args:
            input_path: Path to input file
            output_path: Path to output encrypted file
        """
        with open(input_path, 'rb') as f:
            data = f.read()
        
        encrypted = self.fernet.encrypt(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted)
    
    def decrypt_file(self, input_path: Path, output_path: Path):
        """
        Decrypt a file.
        
        Args:
            input_path: Path to encrypted file
            output_path: Path to output decrypted file
        """
        with open(input_path, 'rb') as f:
            encrypted = f.read()
        
        decrypted = self.fernet.decrypt(encrypted)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted)
    
    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, str]:
        """
        Hash a password using PBKDF2.
        
        Args:
            password: Password to hash
            salt: Optional salt (will generate if not provided)
            
        Returns:
            Tuple of (hashed_password, salt) both as base64 strings
        """
        if salt is None:
            salt = os.urandom(32)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = kdf.derive(password.encode('utf-8'))
        
        return (
            base64.b64encode(key).decode('utf-8'),
            base64.b64encode(salt).decode('utf-8')
        )
    
    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Password to verify
            hashed_password: Base64-encoded hashed password
            salt: Base64-encoded salt
            
        Returns:
            True if password matches, False otherwise
        """
        salt_bytes = base64.b64decode(salt.encode('utf-8'))
        hashed, _ = DataEncryptor.hash_password(password, salt_bytes)
        return hashed == hashed_password
    
    @staticmethod
    def hash_data(data: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """
        Hash data using specified algorithm.
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm (sha256, sha512, md5)
            
        Returns:
            Hexadecimal hash string
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if algorithm == 'sha256':
            return hashlib.sha256(data).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(data).hexdigest()
        elif algorithm == 'md5':
            return hashlib.md5(data).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key.
        
        Returns:
            Base64-encoded encryption key
        """
        return Fernet.generate_key().decode('utf-8')
    
    def get_key(self) -> str:
        """
        Get the current encryption key.
        
        Returns:
            Base64-encoded encryption key
        """
        return self._key.decode('utf-8')


class FieldEncryptor:
    """Encrypt specific fields in dictionaries."""
    
    def __init__(self, encryptor: DataEncryptor, encrypted_fields: Optional[list] = None):
        """
        Initialize field encryptor.
        
        Args:
            encryptor: DataEncryptor instance
            encrypted_fields: List of field names to encrypt
        """
        self.encryptor = encryptor
        self.encrypted_fields = encrypted_fields or [
            'password', 'secret', 'token', 'api_key', 'private_key'
        ]
    
    def encrypt_fields(self, data: dict) -> dict:
        """
        Encrypt specified fields in dictionary.
        
        Args:
            data: Dictionary with fields to encrypt
            
        Returns:
            Dictionary with encrypted fields
        """
        encrypted = data.copy()
        
        for field in self.encrypted_fields:
            if field in encrypted and encrypted[field]:
                encrypted[field] = self.encryptor.encrypt(str(encrypted[field]))
        
        return encrypted
    
    def decrypt_fields(self, data: dict) -> dict:
        """
        Decrypt specified fields in dictionary.
        
        Args:
            data: Dictionary with encrypted fields
            
        Returns:
            Dictionary with decrypted fields
        """
        decrypted = data.copy()
        
        for field in self.encrypted_fields:
            if field in decrypted and decrypted[field]:
                try:
                    decrypted[field] = self.encryptor.decrypt(decrypted[field])
                except Exception:
                    # If decryption fails, leave as is (might not be encrypted)
                    pass
        
        return decrypted