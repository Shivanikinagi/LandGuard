import argparse
import os
import cbor2

from detector.file_type import detect_file_type
from crypto.aes import encrypt_data
from core.ppc_format import PPCFile
from storage.ipfs_client import upload_to_ipfs

def pack_command(args):
    print(f"📦 Packing file: {args.file} with password '{args.password}'")

    # 1. Read file
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return
    with open(args.file, "rb") as f:
        data = f.read()
    print(f"📄 Read {len(data)} bytes")

    # 2. Detect type
    info = detect_file_type(args.file)
    print(f"🔍 Detected type: {info}")

    # 3. Encrypt
    encrypted = encrypt_data(data, args.password)
    payload = cbor2.dumps(encrypted)
    print(f"🔐 Encrypted payload size: {len(payload)} bytes")

    # 4. Wrap in PPC format
    metadata = {
        "original_filename": os.path.basename(args.file),
        "original_mime_type": info.get("mime", "application/octet-stream"),
        "file_type": info.get("type", "unknown"),
        "model_used": "none-yet",
        "encryption_algo": "AES-256-GCM"
    }
    ppc = PPCFile(payload, metadata)
    output_file = os.path.splitext(os.path.basename(args.file))[0] + ".ppc"
    with open(output_file, "wb") as f:
        f.write(ppc.pack())
    print(f"✅ Wrote PPC file: {output_file}")

    # 5. Upload to IPFS
    print(f"🌍 Uploading {output_file} to IPFS via Pinata...")
    try:
        link = upload_to_ipfs(output_file)
        print(f"🌐 IPFS Link: {link}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

def main():
    print("🚀 CLI starting...")
    parser = argparse.ArgumentParser(description="PCC Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Pack
    pack_parser = subparsers.add_parser("pack", help="Encrypt and upload to IPFS")
    pack_parser.add_argument("file", help="Path to the file to pack")
    pack_parser.add_argument("--password", required=True, help="Encryption password")
    pack_parser.set_defaults(func=pack_command)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
