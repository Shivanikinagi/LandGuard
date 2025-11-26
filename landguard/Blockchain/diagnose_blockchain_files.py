"""
Diagnose blockchain module files for issues
"""

import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def diagnose_file(file_path: str) -> dict:
    """Diagnose a single file for issues"""
    path = Path(file_path)
    
    result = {
        "exists": path.exists(),
        "size": 0,
        "has_null_bytes": False,
        "is_utf8": False,
        "is_python": False,
        "first_bytes": "",
        "line_count": 0,
        "error": None
    }
    
    if not path.exists():
        return result
    
    try:
        # Get file size
        result["size"] = path.stat().st_size
        
        # Read as binary
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Check for null bytes
        result["has_null_bytes"] = b'\x00' in content
        
        # Check first 100 bytes
        result["first_bytes"] = repr(content[:100])
        
        # Try UTF-8 decode
        try:
            text = content.decode('utf-8')
            result["is_utf8"] = True
            result["line_count"] = text.count('\n') + 1
            
            # Check if looks like Python
            result["is_python"] = (
                "import " in text or
                "def " in text or
                "class " in text or
                text.strip().startswith("#")
            )
        except UnicodeDecodeError:
            result["is_utf8"] = False
            
    except Exception as e:
        result["error"] = str(e)
    
    return result


def main():
    """Diagnose all blockchain files"""
    console.print("\n[bold cyan]🔍 Blockchain Files Diagnostic[/bold cyan]\n")
    
    files = [
        "blockchain/__init__.py",
        "blockchain/hash_manager.py",
        "blockchain/ipfs_storage.py",
        "blockchain/audit_trail.py",
        "blockchain/digital_signature.py",
        "blockchain/merkle_tree.py",
        "blockchain/evidence_package.py",
        "blockchain/utils.py"
    ]
    
    # Create detailed table
    table = Table(title="📋 File Analysis", box=box.ROUNDED, show_lines=True)
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Size", justify="right")
    table.add_column("Lines", justify="right")
    table.add_column("UTF-8", justify="center")
    table.add_column("Python", justify="center")
    table.add_column("Issues", style="yellow")
    
    issues_found = False
    
    for file_path in files:
        info = diagnose_file(file_path)
        
        if not info["exists"]:
            table.add_row(
                file_path,
                "-",
                "-",
                "-",
                "-",
                "❌ Missing"
            )
            issues_found = True
            continue
        
        # Format size
        size_str = f"{info['size']:,} B"
        if info['size'] == 0:
            size_str = "⚠️ 0 B"
            issues_found = True
        
        # Check for issues
        issues = []
        if info["has_null_bytes"]:
            issues.append("Null bytes")
            issues_found = True
        if not info["is_utf8"]:
            issues.append("Not UTF-8")
            issues_found = True
        if not info["is_python"] and info["size"] > 0:
            issues.append("Not Python?")
            issues_found = True
        if info["error"]:
            issues.append(f"Error: {info['error']}")
            issues_found = True
        
        issues_str = ", ".join(issues) if issues else "✅ OK"
        
        table.add_row(
            file_path,
            size_str,
            str(info["line_count"]),
            "✅" if info["is_utf8"] else "❌",
            "✅" if info["is_python"] else "❌",
            issues_str
        )
    
    console.print(table)
    
    # Print first bytes of problematic files
    console.print("\n[bold]🔬 Detailed Analysis of Problematic Files:[/bold]\n")
    
    for file_path in files:
        info = diagnose_file(file_path)
        
        if info["exists"] and (info["has_null_bytes"] or not info["is_utf8"] or info["size"] == 0):
            console.print(f"[yellow]📄 {file_path}[/yellow]")
            console.print(f"   Size: {info['size']} bytes")
            console.print(f"   First bytes: {info['first_bytes']}")
            console.print()
    
    console.print("="*60)
    
    if issues_found:
        console.print("\n[bold red]⚠️  Issues detected![/bold red]\n")
        console.print("[yellow]Recommended actions:[/yellow]")
        console.print("  1. Run: python fix_blockchain_encoding.py")
        console.print("  2. If files are empty/missing, copy them from artifacts")
        console.print("  3. Ensure files are saved with UTF-8 encoding\n")
    else:
        console.print("\n[bold green]✅ All files look good![/bold green]\n")


if __name__ == "__main__":
    main()