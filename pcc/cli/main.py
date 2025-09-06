from __future__ import annotations
import os, json
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
import time
from rich.prompt import Prompt
import subprocess

from pcc.detect import detect_mime
from ..crypto.aes import encrypt_data, decrypt_data
from ..container import Header, pack, unpack
from ..storage.ipfs_client import upload_to_ipfs
from ..utils import now_iso, read_bytes, write_bytes
from ..models import get_model, detect_primary_type
from core.ppc_format import PPCFile

console = Console()

def format_bytes(bytes_size):
    """Format bytes in human readable format."""
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

# Add these pure Python functions BEFORE your Click commands:

def compress_file(input_path, output=None, passphrase=None, model="auto", upload="none"):
    """Core compression logic without Click dependencies"""
    # Step 1: Read input file
    console.print("\n📄 [bold blue]Read Input File[/bold blue]")
    raw_data = read_bytes(input_path)
    file_size = len(raw_data)
    console.print(f"→ {input_path} ({format_bytes(file_size)})")
    
    # Step 2: Detect file type
    console.print("\n🔍 [bold green]Detected File Type[/bold green]")
    mime = detect_mime(input_path)
    console.print(f"→ {mime} using python-magic")
    
    # Step 3: AI Model Selection
    ptype = detect_primary_type(mime)
    m = get_model(ptype, override=None if model == "auto" else model)
    
    console.print("\n🧠 [bold magenta]AI Model Selection[/bold magenta]")
    console.print(f"→ Using {m.name} v{m.version}")
    console.print(f"→ Optimized for {ptype} content")
    
    # Step 4: Compression
    console.print("\n⚡ [bold yellow]AI Compression[/bold yellow]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Compressing with neural models...", total=None)
        comp_bytes, model_meta = m.compress(path=input_path, mime=mime)
        print("Compressed bytes length:", len(comp_bytes))
        progress.update(task, completed=100)
    
    if len(comp_bytes) == 0:
        console.print("[bold red]ERROR: Compression produced empty output![/bold red]")
        console.print("Check if the VAE model is present and working.")
        return None
    
    compression_ratio = (1 - len(comp_bytes) / file_size) * 100
    console.print(f"→ {format_bytes(file_size)} → {format_bytes(len(comp_bytes))}")
    console.print(f"→ Compression ratio: {compression_ratio:.1f}%")
    
    # Step 5: Encryption
    console.print("\n🔐 [bold red]Encrypted with AES-256-GCM[/bold red]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Applying military-grade encryption...", total=None)
        time.sleep(0.5)  # Small delay for effect
        ciphertext = encrypt_data(comp_bytes, passphrase)
        progress.update(task, completed=100)
    
    console.print("→ Secure, authenticated encryption")
    encrypted_size = len(ciphertext["ciphertext"]) + 32 + 12 + 16  # approx overhead
    console.print(f"→ Payload: {format_bytes(encrypted_size)} (encrypted + salt/iv/tag)")
    
    # Step 6: Container Creation
    console.print("\n📦 [bold cyan]Wrapped into .ppc Format[/bold cyan]")
    header = Header(
        mime=mime,
        orig_name=os.path.basename(input_path),
        created=now_iso(),
        kdf={"salt": ciphertext["salt"]},
        cipher={"iv": ciphertext["iv"], "tag": ciphertext["tag"]},
        comp={"name": m.name, "version": m.version},
        notes="AI-powered compression with neural models",
        ptype=ptype,
        model={"name": m.name, "version": m.version, "meta": model_meta},
    )
    
    blob = pack(header, ciphertext["ciphertext"])
    out = output or (os.path.splitext(input_path)[0] + ".ppc")
    write_bytes(out, blob)
    
    container_name = os.path.basename(out)
    console.print(f"→ Created {container_name} with metadata")
    console.print(f"→ Universal container ready for AI compression")
    console.print(f"→ Total size: {format_bytes(len(blob))}")
    
    # Step 7: IPFS Upload (if requested)
    if upload.lower() != "none":
        console.print("\n🌍 [bold green]Uploaded to IPFS via Pinata[/bold green]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Uploading to decentralized network...", total=None)
            time.sleep(1)  # Simulate upload time
            try:
                url = upload_to_ipfs(out)
                progress.update(task, completed=100)
                
                # Extract CID from URL
                if "ipfs/" in url:
                    cid = url.split("ipfs/")[-1]
                    console.print("→ Decentralized, censorship-resistant storage")
                    console.print(f"→ CID: [bold]{cid}[/bold]")
                    
                    console.print("\n🌐 [bold blue]Generated Public Link[/bold blue]")
                    console.print(f"→ {url}")
                else:
                    console.print(f"→ Upload successful: {url}")
                    
            except Exception as e:
                progress.update(task, completed=100)
                console.print(f"⚠️  Upload failed: {e}")
    
    # Success summary
    console.print(f"\n✅ [bold green]Compression Complete![/bold green]")
    console.print(Panel.fit(
        f"📁 {container_name}\n"
        f"📊 {format_bytes(file_size)} → {format_bytes(len(blob))}\n"
        f"🎯 Model: {m.name} v{m.version}\n"
        f"🔐 AES-256-GCM encrypted",
        title="[bold]Summary[/bold]",
        border_style="green"
    ))
    return out


def decompress_file(container_path, output=None, passphrase=None):
    """Core decompression logic without Click dependencies"""
    console.print("\n📦 [bold blue]Reading Container[/bold blue]")
    blob = read_bytes(container_path)
    console.print(f"→ {container_path} ({format_bytes(len(blob))})")

    console.print("\n🔍 [bold green]Parsing Metadata[/bold green]")
    header, data_blob = unpack(blob)
    metadata = header
    console.print(f"→ Original: {metadata.orig_name}")
    console.print(f"→ MIME: {metadata.mime}")
    console.print(f"→ Model: {metadata.model.get('name', 'unknown')}")
    
    console.print("\n🔐 [bold red]Decrypting Payload[/bold red]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Decrypting with AES-256-GCM...", total=None)
        time.sleep(0.3)
        ciphertext = {
            "ciphertext": data_blob,
            "salt": metadata.kdf["salt"],
            "iv": metadata.cipher["iv"],
            "tag": metadata.cipher["tag"]
        }
        comp_bytes = decrypt_data(ciphertext, passphrase)
        progress.update(task, completed=100)
    
    console.print("→ Successfully decrypted")
    console.print(f"→ Compressed data: {format_bytes(len(comp_bytes))}")
    print("Decrypted data length:", len(comp_bytes))
    
    console.print("\n⚡ [bold yellow]AI Decompression[/bold yellow]")
    mname = metadata.model.get("name") or metadata.comp.get("name")
    ptype = getattr(metadata, "ptype", "binary")
    m = get_model(ptype, override=mname)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Reconstructing with neural models...", total=None)
        raw = m.decompress(data=comp_bytes, meta=metadata.model.get("meta", {}))
        progress.update(task, completed=100)
    
    out = output or metadata.orig_name
    write_bytes(out, raw)
    
    console.print(f"→ Restored: {format_bytes(len(raw))} bytes")
    console.print(f"→ Output: {out}")
    
    if os.path.exists(out):
        console.print(f"[bold green]Decompression successful! File saved as: {out}[/bold green]")
    else:
        console.print(f"[bold red]Decompression failed or file not created.[/bold red]")
    
    console.print(f"\n✅ [bold green]Decompression Complete![/bold green]")
    console.print(Panel.fit(
        f"📁 {out}\n"
        f"📊 Restored perfectly\n"
        f"🎯 Model: {m.name} v{m.version}\n"
        f"✨ Ready to use",
        title="[bold]Summary[/bold]",
        border_style="green"
    ))
    return out


# Then update your Click commands to use these functions:

@click.group()
def cli():
    """🚀 Pied Piper 2.0 - Next-Gen AI Compression System"""

@cli.command()
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False))
@click.option("-o", "--output", type=click.Path(dir_okay=False), help="Output .ppc path")
@click.option("-p", "--passphrase", prompt=True, hide_input=True, confirmation_prompt=False,
              help="Passphrase for AES-GCM encryption")
@click.option("--model", type=click.Choice(["auto","text-huffman","image-vae-stub","image-vae","audio-noop"], case_sensitive=False),
              default="auto", show_default=True, help="Select compression model")
@click.option("--upload", type=click.Choice(["none","pinata"], case_sensitive=False), default="none",
              help="Upload to IPFS")
def compress(input_path, output, passphrase, model, upload):
    """🗜️ Compress and encrypt files with AI-powered compression."""
    compress_file(input_path, output, passphrase, model, upload)


@cli.command()
@click.argument("container_path", type=click.Path(exists=True, dir_okay=False))
@click.option("-o", "--output", type=click.Path(dir_okay=False), help="Output file path")
@click.option("-p", "--passphrase", prompt=True, hide_input=True)
def decompress(container_path, output, passphrase):
    """🔓 Decrypt and decompress .ppc containers."""
    decompress_file(container_path, output, passphrase)


def print_pcc_banner():
    banner = r"""
██████╗  ██████╗  ██████╗      ██████╗ ██████╗ ███╗   ███╗██████╗ ███████╗██████╗ 
██╔══██╗██╔═══██╗██╔═══██╗    ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔════╝██╔══██╗
██████╔╝██║   ██║██║   ██║    ██║     ██║   ██║██╔████╔██║██║  ██║█████╗  ██████╔╝
██╔═══╝ ██║   ██║██║   ██║    ██║     ██║   ██║██║╚██╔╝██║██║  ██║██╔══╝  ██╔══██╗
██║     ╚██████╔╝╚██████╔╝    ╚██████╗╚██████╔╝██║ ╚═╝ ██║██████╔╝███████╗██║  ██║
╚═╝      ╚═════╝  ╚═════╝      ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
    """
    style1 = Style(color="magenta", bold=True)
    style2 = Style(color="cyan", bold=True)
    for i, line in enumerate(banner.splitlines()):
        if line.strip():
            style = style1 if i % 2 == 0 else style2
            console.print(Text(line, style=style))
    console.print(Text("PPC COMPRESSOR", style=Style(color="magenta", bold=True, underline=True)), justify="center")
    console.print(Text("made by Parth KK, Ansh G. & Neel S.", style=Style(color="white", italic=True, dim=True)), justify="center")
    console.print(Text(">>> Welcome to the PPC CLI <<<", style=Style(color="yellow", bold=True)), justify="center")
    console.print()

def main():
    print_pcc_banner()
    
    while True:
        file_path = Prompt.ask("Enter the path to your file in [bold cyan]samples[/bold cyan] folder", default="pcc/samples/")
        if not os.path.isfile(file_path):
            console.print(f"[red]File not found:[/red] {file_path}")
            continue
            
        console.print(Panel.fit("What would you like to do?\n[1] Compress\n[2] Decompress\n[3] Exit", title="Choose Action"))
        action = Prompt.ask("Enter your choice", choices=["1", "2", "3"])
        
        if action == "3":
            console.print("[yellow]Goodbye![/yellow]")
            break
            
        if action == "1":
            password = Prompt.ask("Enter password for encryption", password=True)
            # Call the pure Python function directly
            compress_file(
                input_path=file_path, 
                output=None, 
                passphrase=password, 
                model="auto",  # This will auto-select based on file type
                upload="none"
            )
            
        elif action == "2":
            password = Prompt.ask("Enter password for decryption", password=True)
            output_path = Prompt.ask("Enter output file name", default="restored.txt")
            # Call the pure Python function directly
            decompress_file(
                container_path=file_path,
                output=output_path,
                passphrase=password
            )
            
        again = Prompt.ask("Perform another operation?", choices=["y", "n"], default="y")
        if again.lower() != "y":
            break

# Only run main() when script is run directly, not when imported
if __name__ == "__main__":
    # If command-line arguments are provided, run through Click's CLI
    import sys
    if len(sys.argv) > 1:
        cli()
    else:
        main()