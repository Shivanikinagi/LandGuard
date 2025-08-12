# test_crypto.py
try:
    from crypto.aes import encrypt_data, decrypt_data
    print("✅ Success: encrypt_data and decrypt_data imported!")

    # Test data
    data = b"Hello, Pied Piper!"
    password = "middleout"

    # Encrypt
    encrypted = encrypt_data(data, password)
    print("🔒 Encrypted")

    # Decrypt
    decrypted = decrypt_data(encrypted, password)
    print("🔓 Decrypted:", decrypted.decode('utf-8'))

except Exception as e:
    print(f"❌ Crypto error: {e}")
