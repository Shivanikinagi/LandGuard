#!/usr/bin/env python3
"""
Pied Piper 2.0 - Main CLI Entry Point
Advanced file compression with encryption and IPFS storage
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compressors.compressor import compress_file
from compressors.decompressor import decompress_file
from crypto.aes import encrypt_data, decrypt_data
from storage.ipfs_client import upload_to_ipfs
from core.ppc_format import create_ppc_file, PPCFile
from detector.file_type import detect_file_type

app = typer.Typer(help="🚀 Pied Piper 2.0 - AI-Powered Compression & Storage")
console = Console()


@app.command()
def pack(
    file_path: str = typer.Argument(..., help="Path to the file to compress"),
    password: str = typer.Option(..., "--password", "-p", prompt=True, hide_input=True, help="Encryption password"),
    output: str = typer.Option(None, "--output", "-o", help="Output .ppc file path"),
    upload: bool = typer.Option(True, "--upload/--no-upload", help="Upload to IPFS"),
):
    """
    📦 Compress, encrypt, and optionally upload a file to IPFS
    """
    try:
        # Validate input file
        if not Path(file_path).exists():
            console.print(f"[red]❌ File not found: {file_path}[/red]")
            raise typer.Exit(code=1)
        
        console.print(f"[cyan]✅ Packing: {file_path}[/cyan]")
        
        # Read file
        with open(file_path, "rb") as f:
            original_data = f.read()
        
        original_size = len(original_data)
        console.print(f"[blue]📊 Read {original_size:,} bytes[/blue]")
        
        # Detect file type
        file_info = detect_file_type(file_path)
        console.print(f"[blue]🔍 Detected: {file_info['category']} ({file_info['mime_type']})[/blue]")
        
        # Compress file
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Compressing...", total=None)
            compressed_data, algorithm, compressed_size = compress_file(file_path, file_info)
        
        if compressed_size < original_size:
            ratio = original_size / compressed_size
            console.print(f"[green]📦 Compressed with: {algorithm} → {compressed_size:,} bytes[/green]")
            console.print(f"[green]📈 Compression Ratio: {ratio:.2f}x ({((original_size - compressed_size) / original_size * 100):.1f}% smaller)[/green]")
        else:
            console.print(f"[yellow]📦 Using original data (compression not beneficial)[/yellow]")
            compressed_data = original_data
            algorithm = "none"
            compressed_size = original_size
        
        # Encrypt data
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Encrypting...", total=None)
            encryption_result = encrypt_data(compressed_data, password)
        
        console.print("[green]🔒 Encrypted with AES-256-GCM[/green]")
        
        # Create metadata
        metadata = {
            "original_filename": Path(file_path).name,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_algorithm": algorithm,
            "file_type": file_info['mime_type'],
            "category": file_info['category'],
            "encryption": "AES-256-GCM",
        }
        
        # Determine output path
        if output is None:
            output = f"{file_path}.ppc"
        
        # Create .ppc file
        create_ppc_file(encryption_result['ciphertext'], {
            **metadata,
            "salt": encryption_result['salt'],  # Already base64 encoded
            "iv": encryption_result['iv'],  # Already base64 encoded
            "tag": encryption_result['tag'],  # Already base64 encoded
        }, output)
        
        console.print(f"[green]💾 Created: {output}[/green]")
        
        # Upload to IPFS
        if upload:
            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task(description="Uploading to IPFS...", total=None)
                    ipfs_link = upload_to_ipfs(output)
                
                console.print(f"[green]🌐 IPFS Link: {ipfs_link}[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️ IPFS upload failed: {e}[/yellow]")
                console.print("[yellow]💡 File saved locally. You can upload it later.[/yellow]")
        
        console.print("[green bold]✅ Packing complete![/green bold]")
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def unpack(
    ppc_file: str = typer.Argument(..., help="Path to the .ppc file to decompress"),
    password: str = typer.Option(..., "--password", "-p", prompt=True, hide_input=True, help="Decryption password"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """
    🔓 Decrypt and decompress a .ppc file
    """
    try:
        # Validate input file
        if not Path(ppc_file).exists():
            console.print(f"[red]❌ File not found: {ppc_file}[/red]")
            raise typer.Exit(code=1)
        
        console.print(f"[cyan]🔓 Unpacking: {ppc_file}[/cyan]")
        
        # Read .ppc file
        with open(ppc_file, "rb") as f:
            ppc_data = f.read()
        
        # Unpack .ppc file
        unpacked = PPCFile.unpack(ppc_data)
        header = unpacked['header']
        encrypted_data = unpacked['data']
        
        console.print(f"[blue]📋 Original: {header.get('original_filename', 'unknown')}[/blue]")
        console.print(f"[blue]📊 Size: {header.get('original_size', 0):,} bytes[/blue]")
        console.print(f"[blue]🔧 Algorithm: {header.get('compression_algorithm', 'unknown')}[/blue]")
        
        # Decrypt data
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(description="Decrypting...", total=None)
            
            decrypted_data = decrypt_data({
                'ciphertext': encrypted_data,
                'salt': header['salt'],  # Already base64 encoded string
                'iv': header['iv'],  # Already base64 encoded string
                'tag': header['tag'],  # Already base64 encoded string
            }, password)
        
        console.print("[green]🔑 Decrypted successfully[/green]")
        
        # Decompress data
        algorithm = header.get('compression_algorithm', 'none')
        if algorithm != 'none':
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task(description="Decompressing...", total=None)
                original_data = decompress_file(decrypted_data, algorithm)
            
            console.print(f"[green]📤 Decompressed: {len(decrypted_data):,} → {len(original_data):,} bytes[/green]")
        else:
            original_data = decrypted_data
            console.print("[blue]📤 No decompression needed[/blue]")
        
        # Determine output path
        if output is None:
            original_name = header.get('original_filename', 'restored_file')
            output = f"restored_{original_name}"
        
        # Write output file
        with open(output, "wb") as f:
            f.write(original_data)
        
        console.print(f"[green]💾 Restored: {output}[/green]")
        console.print("[green bold]✅ Unpacking complete![/green bold]")
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        console.print("[yellow]💡 Check your password or file integrity[/yellow]")
        raise typer.Exit(code=1)


@app.command()
def info(
    ppc_file: str = typer.Argument(..., help="Path to the .ppc file"),
):
    """
    📊 Display information about a .ppc file without extracting
    """
    try:
        # Validate input file
        if not Path(ppc_file).exists():
            console.print(f"[red]❌ File not found: {ppc_file}[/red]")
            raise typer.Exit(code=1)
        
        # Read .ppc file
        with open(ppc_file, "rb") as f:
            ppc_data = f.read()
        
        # Unpack .ppc file
        unpacked = PPCFile.unpack(ppc_data)
        header = unpacked['header']
        
        console.print("\n[cyan bold]📦 PPC File Information[/cyan bold]\n")
        console.print(f"[blue]File:[/blue] {ppc_file}")
        console.print(f"[blue]Original Name:[/blue] {header.get('original_filename', 'N/A')}")
        console.print(f"[blue]File Type:[/blue] {header.get('category', 'N/A')} ({header.get('file_type', 'N/A')})")
        console.print(f"[blue]Original Size:[/blue] {header.get('original_size', 0):,} bytes")
        console.print(f"[blue]Compressed Size:[/blue] {header.get('compressed_size', 0):,} bytes")
        
        orig_size = header.get('original_size', 1)
        comp_size = header.get('compressed_size', 1)
        if comp_size < orig_size:
            ratio = orig_size / comp_size
            savings = ((orig_size - comp_size) / orig_size * 100)
            console.print(f"[green]Compression Ratio:[/green] {ratio:.2f}x ({savings:.1f}% smaller)")
        else:
            console.print(f"[yellow]Compression Ratio:[/yellow] 1.0x (no compression)")
        
        console.print(f"[blue]Algorithm:[/blue] {header.get('compression_algorithm', 'N/A')}")
        console.print(f"[blue]Encryption:[/blue] {header.get('encryption', 'N/A')}")
        console.print(f"[blue]Format Version:[/blue] {header.get('version', 'N/A')}\n")
        
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def version():
    """
    📌 Show version information
    """
    console.print("\n[cyan bold]🚀 Pied Piper 2.0[/cyan bold]")
    console.print("[blue]Version:[/blue] 2.0.0")
    console.print("[blue]Phase:[/blue] 1 (Production Ready)")
    console.print("[blue]Features:[/blue]")
    console.print("  • AI-powered compression")
    console.print("  • AES-256-GCM encryption")
    console.print("  • IPFS decentralized storage")
    console.print("  • Custom .ppc container format\n")


if __name__ == "__main__":
    app()
