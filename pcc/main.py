# -*- coding: utf-8 -*-
"""
Pied Piper 2.0 — Universal AI-Powered Compression & Storage
"""
from argparse import _SubParsersAction
import os
import sys  # Import the sys module
import typer
from pathlib import Path
import cbor2
from core.ppc_format import PPCFile


# Import detector module with inline definition as fallback
try:
    from detector.file_type import detect_file_type
except:
    # Inline fallback detector function
    import mimetypes
    
    def detect_file_type(file_path: str) -> dict:
        path = Path(file_path)
        ext = path.suffix.lower()
        mime, _ = mimetypes.guess_type(file_path)
        
        if ext in [".txt", ".md", ".rtf", ".log"]:
            ftype = "text"
        elif ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"]:
            ftype = "image"
        elif ext in [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"]:
            ftype = "audio"
        elif ext in [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"]:
            ftype = "video"
        elif ext in [".pdf"]:
            ftype = "pdf"
        elif ext in [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"]:
            ftype = "archive"
        elif ext in [".csv", ".xls", ".xlsx"]:
            ftype = "spreadsheet"
        elif ext in [".json", ".xml", ".yaml", ".yml"]:
            ftype = "data"
        elif ext in [".py", ".java", ".cpp", ".c", ".js", ".ts", ".html", ".css"]:
            ftype = "code"
        else:
            ftype = "binary"
        
        return {
            "type": ftype,
            "mime": mime if mime else "application/octet-stream"
        }

# Import modules with inline fallbacks to avoid null bytes issues
try:
    from crypto.aes import encrypt_data, decrypt_data
except:
    # Inline AES encryption fallback
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import os
    
    def derive_key(password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
        return kdf.derive(password.encode())
    
    def encrypt_data(data: bytes, password: str) -> dict:
        salt = os.urandom(16)
        iv = os.urandom(12)
        key = derive_key(password, salt)
        encryptor = Cipher(algorithms.AES(key), modes.GCM(iv)).encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        return {"ciphertext": ciphertext, "iv": iv, "salt": salt, "tag": encryptor.tag}
    
    def decrypt_data(encrypted: dict, password: str) -> bytes:
        key = derive_key(password, encrypted["salt"])
        decryptor = Cipher(algorithms.AES(key), modes.GCM(encrypted["iv"], encrypted["tag"])).decryptor()
        return decryptor.update(encrypted["ciphertext"]) + decryptor.finalize()

try:
    from core.ppc_format import PPCFile
except:
    # Inline PPC format fallback
    import struct
    import json
    
    class PPCFile:
        def __init__(self, data: bytes, metadata: dict):
            self.data = data
            self.metadata = metadata
        
        def pack(self) -> bytes:
            header = json.dumps(self.metadata).encode('utf-8')
            header_len = len(header)
            return struct.pack('<I', header_len) + header + self.data
        
        @staticmethod
        def unpack(data: bytes) -> dict:
            header_len = struct.unpack('<I', data[:4])[0]
            header = json.loads(data[4:4+header_len].decode('utf-8'))
            payload = data[4+header_len:]
            return {"header": header, "data": payload}

try:
    sys.path.append('..')
    from storage.ipfs_client import upload_to_ipfs
except:
    # Inline IPFS fallback with real Pinata API
    import requests
    
    def upload_to_ipfs(file_path: str) -> str:
        try:
            # Install requests if not available
            try:
                import requests
            except ImportError:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
                import requests
            
            PINATA_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySW5mb3JtYXRpb24iOnsiaWQiOiIxYTU1ZGM2My1iYzM0LTRlZjUtOGFhMy1mNDM0OWI1M2M4NzgiLCJlbWFpbCI6InBhcnRoMTIyMDA0QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJwaW5fcG9saWN5Ijp7InJlZ2lvbnMiOlt7ImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxLCJpZCI6IkZSQTEifSx7ImRlc2lyZWRSZXBsaWNhdGlvbkNvdW50IjoxLCJpZCI6Ik5ZQzEifV0sInZlcnNpb24iOjF9LCJtZmFfZW5hYmxlZCI6ZmFsc2UsInN0YXR1cyI6IkFDVElWRSJ9LCJhdXRoZW50aWNhdGlvblR5cGUiOiJzY29wZWRLZXkiLCJzY29wZWRLZXlLZXkiOiJmOTFmZDY4OWQzZGJlNTdmYTRlYyIsInNjb3BlZEtleVNlY3JldCI6IjdlNGRjNTM3MWY5MmQ1ZDRkMjdiMTQ5Yjg0MGUwN2VkZjk1YzQzNjE1Mjc3MzY3YTY4ODIxMDI1MTZiYzU0NzMiLCJleHAiOjE3ODc0NjQwNTN9.4sblpV6zSLFnOiPGYQ8XEIEv8X_RaDun8KRLi4cX-yQ"
            
            url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
            headers = {"Authorization": f"Bearer {PINATA_JWT}"}
            
            print(f"🌐 Uploading to IPFS via Pinata...")
            
            with open(file_path, "rb") as f:
                response = requests.post(url, files={"file": f}, headers=headers, timeout=30)
            
            print(f"📡 Pinata response: {response.status_code}")
            
            if response.status_code == 200:
                cid = response.json()["IpfsHash"]
                return f"https://gateway.pinata.cloud/ipfs/{cid}"
            else:
                print(f"❌ Pinata error: {response.text}")
                return f"ipfs://upload-failed-{response.status_code}-{os.path.basename(file_path)}"
        except Exception as e:
            print(f"❌ IPFS upload error: {e}")
            return f"ipfs://error-{os.path.basename(file_path)}"

# --- AI Module Loading with Fallbacks ---
compress_file = None  # Will be defined below
decompress_data = None

try:
    from compressors.compressor import compress_file
    from compressors.decompressor import decompress_data
    print("✅ AI compressor loaded")
except ImportError as e:
    print(f"🟡 AI not available (ImportError): {e}")
except Exception as e:
    print(f"❌ Unexpected error loading AI: {e}")

if decompress_data is None:
    def decompress_data(data, metadata):
        model_used = metadata.get("model_used", "none")
        if model_used != "none":
            raise ImportError(f"Decompression for model '{model_used}' not available.")
        return data

# Define fallback if not already defined
if compress_file is None:
    def compress_file(file_path: str, file_info: dict, model_hint: str = None):
        print("⚠️  No AI model — using original data (no compression)")
        with open(file_path, "rb") as f:
            data = f.read()
        return data, "none", len(data)

# ✅ Define the Typer app AFTER imports and function setup
app = typer.Typer(
    name="ppc",
    help="Pied Piper Compressed (PPC) — AI-powered universal compression & decentralized storage"
)

@app.command()
def pack(
    file_path: str = typer.Argument(..., help="Path to the file to compress and upload"),
    password: str = typer.Option(None, "--password", "-p", prompt=True, hide_input=True, help="Encryption password"),
    model: str = typer.Option(None, "--model", "-m", help="AI model to use: 'vae', 'bpe', or 'auto'"),
):
    """
    Compress, encrypt, and upload a file to IPFS as .ppc
    """
    typer.echo(f"🚀 Packing: {file_path}")
    
    if not os.path.exists(file_path):
        typer.echo(f"❌ File not found: {file_path}")
        return

    # Read file
    with open(file_path, "rb") as f:
        original_data = f.read()
    typer.echo(f"📄 Read {len(original_data)} bytes")

    # Detect file type
    file_info = detect_file_type(file_path)
    typer.echo(f"✅ Detected: {file_info['type']} ({file_info['mime']})")

    # Compression
    try:
        compressed_data, model_meta = compress_file(file_path, file_info, model)
        compressed_size = len(compressed_data)
        model_used = model_meta.get("name", "none")
        typer.echo(f"🧠 Compressed with: {model_used} → {compressed_size} bytes")
    except Exception as e:
        typer.echo(f"⚠️  {e}")
        compressed_data = original_data
        compressed_size = len(original_data)
        model_used = "none"
        model_meta = {}

    # Define metadata BEFORE using it
    metadata = {
        "original_filename": Path(file_path).name,
        "original_mime_type": file_info["mime"],
        "file_type": file_info["type"],
        "model_used": model_used,
        "original_size_bytes": len(original_data),
        "compressed_size_bytes": compressed_size,
        "compression_ratio": len(original_data) / max(compressed_size, 1)
    }

    # Encryption
    if password:
        encrypted = encrypt_data(compressed_data, password)
        typer.echo(f"🔐 Encrypted")
    else:
        encrypted = {"ciphertext": compressed_data, "salt": "", "iv": "", "tag": ""}
        typer.echo(f"⚠️  Not encrypted (no password)")

    # NOW use the metadata to create PPC file
    try:
        ppc = PPCFile(encrypted["ciphertext"], metadata)
        ppc_blob = ppc.pack()
        
        output_path = file_path + ".ppc"
        with open(output_path, "wb") as f:
            f.write(ppc_blob)
        typer.echo(f"📦 Saved to {output_path}")
    except Exception as e:
        typer.echo(f"❌ Packing failed: {e}")

    # --- UPLOAD TO IPFS ---
    try:
        link = upload_to_ipfs(output_path)
        typer.echo(f"🌐 IPFS Link: {link}")
    except Exception as e:
        typer.echo(f"⚠️  Upload failed: {e}")
        raise typer.Exit(1)


@app.command()
def unpack(
    ppc_path: str = typer.Argument(..., help="Path to the .ppc file to unpack."),
    password: str = typer.Option(None, "--password", "-p", help="Decryption password (if required)."),
    output_path: str = typer.Option(None, "--output", "-o", help="Optional: Path to save the unpacked file."),
):
    """
    Unpack a .ppc file to its original state.
    """
    typer.echo(f"📦 Unpacking: {ppc_path}")
    if not os.path.exists(ppc_path):
        typer.echo(f"❌ File not found: {ppc_path}")
        raise typer.Exit(1)

    # --- READ AND UNPACK .PPC ---
    try:
        with open(ppc_path, "rb") as f:
            raw_ppc_data = f.read()
        unpacked = PPCFile.unpack(raw_ppc_data)
        metadata = unpacked["header"]
        data_blob = unpacked["data"]
        typer.echo("✅ .ppc file format is valid.")
    except Exception as e:
        typer.echo(f"❌ Failed to read or parse .ppc file: {e}")
        raise typer.Exit(1)

    # --- DECRYPTION ---
    decrypted_data = data_blob
    if metadata.get("encryption_algo"):
        try:
            # Existing decryption code
            decrypted_data = decrypt_data(encrypted_data, password)
            typer.echo("✅ Successfully decrypted")
        except Exception as e:
            typer.echo(f"❌ [bold red]DECRYPTION FAILED: {e}[/bold red]")
            typer.echo("This usually means the password is incorrect.")
            return

    # --- DECOMPRESSION ---
    try:
        original_data = decompress_data(decrypted_data, metadata)
        typer.echo(f"🧠 Decompressed with: {metadata['model_used']}")
    except Exception as e:
        typer.echo(f"❌ Decompression failed: {e}")
        raise typer.Exit(1)

    # --- SAVE ORIGINAL FILE ---
    if output_path is None:
        # Use the original filename from metadata, save in current dir
        output_path = metadata.get("original_filename", "unpacked_file")
    try:
        with open(output_path, "wb") as f:
            f.write(original_data)
        typer.echo(f"🎉 Successfully unpacked to: {output_path}")
    except Exception as e:
        typer.echo(f"❌ Failed to write output file: {e}")
        raise typer.Exit(1)

@app.command()
def info(
    ppc_path: str = typer.Argument(..., help="Path to the .ppc file")
):
    """
    Show metadata of a .ppc file
    """
    if not os.path.exists(ppc_path):
        typer.echo("❌ File not found")
        raise typer.Exit(1)

    try:
        from core.ppc_format import PPCFile
        with open(ppc_path, "rb") as f:
            raw = f.read()
        decoded = PPCFile.unpack(raw)
        header = decoded["header"]

        typer.echo("\n📄 .PPC FILE INFO")
        typer.echo("=" * 50)
        import json
        typer.echo(json.dumps(header, indent=2))
    except Exception as e:
        typer.echo(f"❌ Invalid .ppc file: {e}")
        raise typer.Exit(1)


# ======================
# Run with: python main.py --help
# ======================
if __name__ == "__main__":
    app()

def unpack_command(args):
    print(f"📦 Unpacking: {args.file} with password '{args.password}'")

    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return

    with open(args.file, "rb") as f:
        raw = f.read()

    # Unpack PPC
    unpacked = PPCFile.unpack(raw)
    header = unpacked["header"]
    payload = unpacked["data"]

    print(f"🔍 Metadata: {header}")

    # Decrypt
    import cbor2
    encrypted = cbor2.loads(payload)
    from crypto.aes import decrypt_data
    data = decrypt_data(encrypted, args.password)

    # Write output
    output_file = header.get("original_filename", "restored_file")
    with open(output_file, "wb") as f:
        f.write(data)
    print(f"✅ Restored file: {output_file}")

# Add to argparse
unpack_parser = _SubParsersAction.add_parser("unpack", help="Decrypt and restore file")
unpack_parser.add_argument("file", help="Path to the .ppc file")
unpack_parser.add_argument("--password", required=True, help="Decryption password")
unpack_parser.set_defaults(func=unpack_command)