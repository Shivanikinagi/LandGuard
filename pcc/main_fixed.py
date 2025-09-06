# -*- coding: utf-8 -*-
"""
Pied Piper 2.0 — Universal AI-Powered Compression & Storage
"""
import os
import sys
import typer
from pathlib import Path
import cbor2

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use local detector module first, fallback to parent
try:
    from detector.file_type import detect_file_type
except:
    sys.path.append('..')
    from detector.file_type import detect_file_type

from crypto.aes import encrypt_data, decrypt_data
from core.ppc_format import PPCFile
from storage.ipfs_client import upload_to_ipfs

# --- AI Module Loading with Fallbacks ---
compress_file = None
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

if compress_file is None:
    def compress_file(file_path: str, file_info: dict, model_hint: str = None):
        print("⚠️  No AI model — using original data (no compression)")
        with open(file_path, "rb") as f:
            data = f.read()
        return data, "none", len(data)

# ✅ Define the Typer app
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
        typer.echo("❌ File not found")
        raise typer.Exit(1)

    try:
        with open(file_path, "rb") as f:
            original_data = f.read()
        typer.echo(f"📄 Read {len(original_data)} bytes")
    except Exception as e:
        typer.echo(f"❌ Failed to read file: {e}")
        raise typer.Exit(1)

    try:
        file_info = detect_file_type(file_path)
        typer.echo(f"✅ Detected: {file_info['type']} ({file_info['mime']})")
    except Exception as e:
        typer.echo(f"❌ Detection failed: {e}")
        raise typer.Exit(1)

    # --- AI COMPRESSION ---
    try:
        compressed_data, model_used, compressed_size = compress_file(file_path, file_info, model)
        typer.echo(f"🧠 Compressed with: {model_used} → {compressed_size} bytes")
    except Exception as e:
        typer.echo(f"❌ Compression failed: {e}")
        compressed_data, model_used, compressed_size = original_data, "none", len(original_data)

    # --- METADATA ---
    metadata = {
        "original_filename": Path(file_path).name,
        "original_mime_type": file_info["mime"],
        "file_type": file_info["type"],
        "model_used": model_used,
        "original_size_bytes": len(original_data),
        "compressed_size_bytes": compressed_size,
        "compression_ratio": len(original_data) / max(compressed_size, 1)
    }

    # --- ENCRYPTION ---
    if password:
        try:
            encrypted = encrypt_data(compressed_data, password)
            final_data = cbor2.dumps(encrypted)
            metadata["encryption_algo"] = "AES-256-GCM"
            typer.echo("🔐 Encrypted")
        except Exception as e:
            typer.echo(f"❌ Encryption failed: {e}")
            raise typer.Exit(1)
    else:
        final_data = compressed_data

    # --- WRAP IN .PPC ---
    try:
        ppc = PPCFile(final_data, metadata)
        output_path = file_path + ".ppc"
        with open(output_path, "wb") as f:
            f.write(ppc.pack())
        typer.echo(f"📦 Created: {output_path}")
        typer.echo(f"📊 Compression Ratio: {metadata['compression_ratio']:.2f}x")
    except Exception as e:
        typer.echo(f"❌ Packing failed: {e}")
        raise typer.Exit(1)

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
        typer.echo(f"🔐 File is encrypted with {metadata['encryption_algo']}. Password needed.")
        if not password:
            password = typer.prompt("Enter password", hide_input=True)
        try:
            encrypted_dict = cbor2.loads(data_blob)
            decrypted_data = decrypt_data(encrypted_dict, password)
            typer.echo("✅ Decryption successful.")
        except Exception as e:
            typer.echo(f"❌ Decryption failed: {e}. Incorrect password?")
            raise typer.Exit(1)

    # --- DECOMPRESSION ---
    try:
        original_data = decompress_data(decrypted_data, metadata)
        typer.echo(f"🧠 Decompressed with: {metadata['model_used']}")
    except Exception as e:
        typer.echo(f"❌ Decompression failed: {e}")
        raise typer.Exit(1)

    # --- SAVE ORIGINAL FILE ---
    if output_path is None:
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

if __name__ == "__main__":
    app()
