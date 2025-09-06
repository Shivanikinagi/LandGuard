# -*- coding: utf-8 -*-
# read_pcc.py
from core.ppc_format import PPCFile
import json
import os
import requests

# === Option 1: Load from LOCAL file (recommended)
# Make sure you've downloaded the .ppc file first
LOCAL_FILE_PATH = "downloaded.ppc"  # ← Rename your downloaded file to this

# === Option 2: Download directly from IPFS
CID = "QmcZm7faqtoXrVECPmhmefogFv8ZnF6z92GCeJikdWg3ZL"
IPFS_GATEWAY = "https://gateway.pinata.cloud/ipfs/"

def download_from_ipfs(cid: str, output_path: str):
    url = f"{IPFS_GATEWAY}{cid}"
    print(f"📥 Downloading from: {url}")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Saved as {output_path}")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        raise

# Choose one method:

# --- METHOD A: Use local file (if already downloaded)
if os.path.exists(LOCAL_FILE_PATH):
    print(f"📄 Loading local file: {LOCAL_FILE_PATH}")
    with open(LOCAL_FILE_PATH, "rb") as f:
        raw = f.read()
else:
    print(f"⚠️  Local file not found: {LOCAL_FILE_PATH}")
    print("🔁 Attempting to download from IPFS...")
    download_from_ipfs(CID, LOCAL_FILE_PATH)
    with open(LOCAL_FILE_PATH, "rb") as f:
        raw = f.read()

# --- Parse .ppc ---
try:
    decoded = PPCFile.unpack(raw)
    print("\n📄 .PPC METADATA")
    print("=" * 50)
    print(json.dumps(decoded["header"], indent=2))

    payload = decoded["payload"]
    print(f"\n🔐 ENCRYPTED PAYLOAD: {len(payload)} bytes")
    print("💡 Tip: Use decrypt.py to decrypt with password")

except Exception as e:
    print(f"❌ Failed to parse .ppc file: {e}")
    print("💡 This could be due to:")
    print("   - Corrupted download")
    print("   - Truncated file")
    print("   - Wrong encoding (save .py files as UTF-8 without BOM)")