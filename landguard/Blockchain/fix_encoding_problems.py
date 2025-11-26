"""
Fix encoding issues in blockchain module files
This script will clean null bytes and ensure UTF-8 encoding
"""

import os
from pathlib import Path
from rich.console import Console
from rich.progress import track

console = Console()


def clean_file(file_path: str) -> bool:
    """
    Clean a Python file of null bytes and ensure UTF-8 encoding
    Returns True if file was fixed, False if no issues found
    """
    path = Path(file_path)
    
    if not path.exists():
        console.print(f"[yellow]⏭️  Skipping {file_path} (not found)[/yellow]")
        return False
    
    try:
        # Read file as binary
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Check for null bytes
        has_null_bytes = b'\x00' in content
        
        # Try to decode and re-encode as UTF-8
        try:
            text = content.decode('utf-8')
            needs_cleaning = has_null_bytes
        except UnicodeDecodeError:
            # Try with error handling
            text = content.decode('utf-8', errors='ignore')
            needs_cleaning = True
        
        if needs_cleaning:
            # Remove null bytes
            text = text.replace('\x00', '')
            
            # Create backup
            backup_path = path.with_suffix('.bak')
            with open(backup_path, 'wb') as f:
                f.write(content)
            
            # Write cleaned content
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(text)
            
            console.print(f"[green]✅ Fixed {file_path}[/green] (backup: {backup_path})")
            return True
        else:
            console.print(f"[dim]✓  {file_path} is already clean[/dim]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Error processing {file_path}: {e}[/red]")
        return False


def main():
    """Clean all blockchain module files"""
    console.print("\n[bold cyan]🔧 Blockchain Module Encoding Fixer[/bold cyan]\n")
    
    files_to_clean = [
        "blockchain/__init__.py",
        "blockchain/hash_manager.py",
        "blockchain/ipfs_storage.py",
        "blockchain/audit_trail.py",
        "blockchain/digital_signature.py",
        "blockchain/merkle_tree.py",
        "blockchain/evidence_package.py",
        "blockchain/utils.py"
    ]
    
    console.print(f"Scanning {len(files_to_clean)} files...\n")
    
    fixed_count = 0
    for file_path in track(files_to_clean, description="Processing files"):
        if clean_file(file_path):
            fixed_count += 1
    
    console.print("\n" + "="*60)
    
    if fixed_count > 0:
        console.print(f"\n[bold green]✅ Fixed {fixed_count} file(s)[/bold green]")
        console.print("[yellow]Backups created with .bak extension[/yellow]")
        console.print("\nRun verification again: python verify_blockchain_setup.py")
    else:
        console.print("\n[bold green]✅ All files are already clean![/bold green]")
    
    console.print()


if __name__ == "__main__":
    main()