# crypto/aes.py


from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


from cryptography.hazmat.primitives import hashes


from cryptography.hazmat.backends import default_backend


import os


import base64





def encrypt_data(data: bytes, passphrase: str) -> dict:


    """


    Encrypt data using AES-256-GCM with PBKDF2 key derivation


    """


    # Generate random salt and IV


    salt = os.urandom(32)


    iv = os.urandom(12)  # GCM uses 96-bit IV


    


    # Derive key from passphrase


    kdf = PBKDF2HMAC(


        algorithm=hashes.SHA256(),


        length=32,


        salt=salt,


        iterations=100000,


        backend=default_backend()


    )


    key = kdf.derive(passphrase.encode())


    


    # Encrypt


    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())


    encryptor = cipher.encryptor()


    ciphertext = encryptor.update(data) + encryptor.finalize()


    


    return {


        "ciphertext": ciphertext,


        "salt": base64.b64encode(salt).decode(),


        "iv": base64.b64encode(iv).decode(),


        "tag": base64.b64encode(encryptor.tag).decode()


    }





def decrypt_data(encrypted_data: dict, passphrase: str) -> bytes:


    """


    Decrypt data using AES-256-GCM


    """


    # Decode base64 values


    salt = base64.b64decode(encrypted_data["salt"])


    iv = base64.b64decode(encrypted_data["iv"])


    tag = base64.b64decode(encrypted_data["tag"])


    ciphertext = encrypted_data["ciphertext"]


    


    # Derive key from passphrase


    kdf = PBKDF2HMAC(


        algorithm=hashes.SHA256(),


        length=32,


        salt=salt,


        iterations=100000,


        backend=default_backend()


    )


    key = kdf.derive(passphrase.encode())


    


    # Decrypt


    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())


    decryptor = cipher.decryptor()


    return decryptor.update(ciphertext) + decryptor.finalize()