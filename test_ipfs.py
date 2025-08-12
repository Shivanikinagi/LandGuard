from storage.ipfs_client import upload_to_ipfs

if __name__ == "__main__":
    file_path = "samples/test.txt"

    try:
        print(f"📤 Uploading {file_path} to IPFS via Pinata...")
        ipfs_url = upload_to_ipfs(file_path)
        print("✅ Upload successful!")
        print(f"🌐 IPFS Gateway URL: {ipfs_url}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
