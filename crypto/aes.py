# crypto/aes.py
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import cbor2

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return kdf.derive(password.encode())

def encrypt_data(data: bytes, password: str) -> dict:
    """
    Encrypt data using AES-256-GCM and return encrypted components
    """
    salt = os.urandom(16)
    iv = os.urandom(12)
    key = derive_key(password, salt)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv)).encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    return {
        "ciphertext": ciphertext,
        "iv": iv,
        "salt": salt,
        "tag": encryptor.tag
    }

def decrypt_data(encrypted: dict, password: str) -> bytes:
    """
    Decrypt data using AES-256-GCM
    """
    key = derive_key(password, encrypted["salt"])
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(encrypted["iv"], encrypted["tag"])
    ).decryptor()
    return decryptor.update(encrypted["ciphertext"]) + decryptor.finalize()