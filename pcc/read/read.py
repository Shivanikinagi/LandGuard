# read.py
import cbor2
import sys
from pathlib import Path

# HACK: Add project root and pcc directory to path to allow imports.
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(1, str(project_root / "pcc"))

from crypto.aes import decrypt_data
from core.ppc_format import PPCFile
import cbor2

# Load and parse
with open("downloaded.ppc", "rb") as f:
    raw = f.read()

decoded = PPCFile.unpack(raw)
data_blob = decoded["data"]
header = decoded["header"]

# Decrypt
encrypted_blob = cbor2.loads(data_blob)
password = "middleout"  # ← Use the correct password

try:
    decrypted = decrypt_data(encrypted_blob, password)
    print("🔓 DECRYPTED CONTENT:")
    print(decrypted.decode('utf-8'))
except Exception as e:
    print("❌ Decryption failed:", str(e))