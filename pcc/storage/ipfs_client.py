# -*- coding: utf-8 -*-
"""
storage/ipfs_client.py
Handles file uploads to IPFS via Pinata using a secure JWT stored in .env.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve Pinata JWT from environment
PINATA_JWT = os.getenv("PINATA_JWT")

if not PINATA_JWT:
    raise EnvironmentError(
        "❌ PINATA_JWT not found in .env.\n"
        "Add this line to your .env file:\n"
        "PINATA_JWT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxx"
    )

def upload_to_ipfs(file_path: str) -> str:
    """
    Upload a file to IPFS via Pinata.
    Returns the public gateway link to the uploaded file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ File not found: {file_path}")

    url ="https://api.pinata.cloud/pinning/pinFileToIPFS"

    headers = {
        "Authorization": f"Bearer {PINATA_JWT}"
    }

    try:
        with open(file_path, "rb") as file:
            response = requests.post(
                url,
                files={"file": file},
                headers=headers,
                timeout=30
            )

        if response.status_code == 401:
            raise PermissionError("❌ Unauthorized: Invalid or expired Pinata JWT")
        elif response.status_code == 413:
            raise ValueError("❌ File too large for Pinata (free tier: ~100MB limit)")
        elif response.status_code != 200:
            raise RuntimeError(f"❌ Pinata API error {response.status_code}: {response.text}")

        cid = response.json().get("IpfsHash")
        if not cid:
            raise RuntimeError("❌ Pinata response missing IpfsHash")

        return f"https://gateway.pinata.cloud/ipfs/{cid}"

    except requests.exceptions.ConnectionError:
        raise ConnectionError("❌ Network error: Check your internet connection")
    except requests.exceptions.Timeout:
        raise TimeoutError("❌ Upload timed out")
    except Exception as e:
        raise RuntimeError(f"❌ Upload failed: {e}")
    
    
   
    
