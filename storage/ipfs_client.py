# storage/ipfs_client.py
import requests

# Pinata API details
PINATA_API_KEY = "8874f676694fbff56c1c"
PINATA_API_SECRET = "a80ca47f4de45c1d331f27d03d93606146a142293078723d0beb764a71908b4d"
PINATA_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiIzYWJjZmZkMi1mYzM2LTQyYTUtODVkMS1hMDc0NTUyMDVkM2YiLCJlbWFpbCI6InBhcnRoOTU0NWtrQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaW5fcG9saWN5Ijp7InJlZ2lvbnMiOlt7ImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxLCJpZCI6IkZSQTEifSx7ImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxLCJpZCI6Ik5ZQzEifV0sInZlcnNpb24iOjF9LCJtZmFfZW5hYmxlZCI6ZmFsc2UsInN0YXR1cyI6IkFDVElWRSJ9LCJhdXRoZW50aWNhdGlvblR5cGUiOiJzY29wZWRLZXkiLCJzY29wZWRLZXlLZXkiOiI4ODc0ZjY3NjY5NGZiZmY1NmMxYyIsInNjb3BlZEtleVNlY3JldCI6ImE4MGNhNDdmNGRlNDVjMWQzMzFmMjdkMDNkOTM2MDYxNDZhMTQyMjkzMDc4NzIzZDBiZWI3NjRhNzE5MDhiNGQiLCJleHAiOjE3ODY1MjU0NzZ9.1TPbRgGVSHagRI1UXjmdrr8k_X9vWnr-BmRQ34-DI2c"  
# Or use API key/secret

def upload_to_ipfs(file_path: str) -> str:
    """
    Upload a file to IPFS via Pinata and return the CID + public link
    """
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    
    headers = {
        # Option A: Use JWT (recommended)
        "Authorization": f"Bearer {PINATA_JWT}"
        
        # Option B: Use API key/secret (less secure)
        # "pinata_api_key": PINATA_API_KEY,
        # "pinata_secret_api_key": PINATA_API_SECRET,
    }
    
    with open(file_path, "rb") as f:
        response = requests.post(
            url,
            files={"file": f},
            headers=headers
        )
    
    if response.status_code == 200:
        cid = response.json()["IpfsHash"]
        return f"https://gateway.pinata.cloud/ipfs/{cid}"
    else:
        raise Exception(f"Pinata upload failed: {response.status_code} - {response.text}")