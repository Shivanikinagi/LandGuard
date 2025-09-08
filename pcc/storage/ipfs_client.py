# -*- coding: utf-8 -*-
# storage/ipfs_client.py
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve Pinata JWT from environment
PINATA_JWT = os.getenv("PINATA_JWT")

if not PINATA_JWT:
    raise ValueError(
        "PINATA_JWT not found. Please set it in a .env file:\n"
        "PINATA_JWT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx"
    )

def upload_to_ipfs(file_path: str) -> str:
    """
    Upload a file to IPFS via Pinata.
    Returns a public gateway link.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"  # ✅ No trailing space

    headers = {
        "Authorization": f"Bearer {PINATA_JWT}"
    }

    try:
        with open(file_path, "rb") as file:
            response = requests.post(
                url,
                files={"file": file},
                headers=headers,
                timeout=30  # Prevent hanging
            )

        # Debug: print status and response
        if response.status_code == 401:
            raise Exception("❌ Unauthorized: Invalid or expired Pinata JWT")
        elif response.status_code == 413:
            raise Exception("❌ File too large for Pinata (free tier: ~100MB)")
        elif response.status_code != 200:
            raise Exception(f"❌ Pinata API error {response.status_code}: {response.text}")

        cid = response.json()["IpfsHash"]
        link = f"https://gateway.pinata.cloud/ipfs/{cid}"  # ✅ No trailing space
        return link

    except requests.exceptions.ConnectionError:
        raise Exception("❌ Network error: Check your internet connection")
    except requests.exceptions.Timeout:
        raise Exception("❌ Upload timed out")
    except Exception as e:
        raise Exception(f"❌ Upload failed: {str(e)}")