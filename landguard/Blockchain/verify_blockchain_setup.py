"""
Verify LandGuard Phase 5 Blockchain Setup
Run this script to check if everything is configured correctly
"""

import os
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def check_directories():
    """Check if all required directories exist"""
    required_dirs = [
        "blockchain/storage/hashes",
        "blockchain/storage/audit_logs",
        "blockchain/storage/signatures",
        "blockchain/storage/batches",
        "blockchain/storage/evidence",
        "blockchain/logs"
    ]
    
    table = Table(title="📁 Directory Structure", box=box.ROUNDED)
    table.add_column("Directory", style="cyan")
    table.add_column("Status", style="bold")
    
    all_exist = True
    for directory in required_dirs:
        exists = Path(directory).exists()
        status = "✅ Exists" if exists else "❌ Missing"
        table.add_row(directory, status)
        if not exists:
            all_exist = False
    
    console.print(table)
    return all_exist


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        "cryptography",
        "requests",
        "yaml",
        "cbor2"
    ]
    
    table = Table(title="📦 Dependencies", box=box.ROUNDED)
    table.add_column("Package", style="cyan")
    table.add_column("Status", style="bold")
    
    all_installed = True
    for package in required_packages:
        try:
            __import__(package)
            table.add_row(package, "✅ Installed")
        except ImportError:
            table.add_row(package, "❌ Missing")
            all_installed = False
    
    console.print(table)
    return all_installed


def check_config_files():
    """Check if configuration files exist"""
    config_files = [
        "blockchain_config.yaml",
        ".env"
    ]
    
    table = Table(title="⚙️ Configuration Files", box=box.ROUNDED)
    table.add_column("File", style="cyan")
    table.add_column("Status", style="bold")
    
    all_exist = True
    for config_file in config_files:
        exists = Path(config_file).exists()
        status = "✅ Exists" if exists else "❌ Missing"
        table.add_row(config_file, status)
        if not exists:
            all_exist = False
    
    console.print(table)
    return all_exist


def check_env_variables():
    """Check if environment variables are set"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        console.print("[yellow]Note: python-dotenv not installed, reading from system env only[/yellow]")
    
    required_vars = [
        "PINATA_API_KEY",
        "PINATA_SECRET_KEY"
    ]
    
    table = Table(title="🔐 Environment Variables", box=box.ROUNDED)
    table.add_column("Variable", style="cyan")
    table.add_column("Status", style="bold")
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            table.add_row(var, "✅ Set")
        else:
            table.add_row(var, "❌ Not Set")
            all_set = False
    
    console.print(table)
    return all_set


def check_blockchain_files():
    """Check if blockchain module files exist"""
    modules = [
        "blockchain/__init__.py",
        "blockchain/hash_manager.py",
        "blockchain/ipfs_storage.py",
        "blockchain/audit_trail.py",
        "blockchain/digital_signature.py",
        "blockchain/merkle_tree.py",
        "blockchain/evidence_package.py",
        "blockchain/utils.py"
    ]
    
    table = Table(title="🔗 Blockchain Module Files", box=box.ROUNDED)
    table.add_column("File", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Size", style="dim")
    
    all_exist = True
    for module_file in modules:
        path = Path(module_file)
        if path.exists():
            size = path.stat().st_size
            if size == 0:
                table.add_row(module_file, "⚠️ Empty", "0 bytes")
            else:
                table.add_row(module_file, "✅ Exists", f"{size:,} bytes")
        else:
            table.add_row(module_file, "❌ Missing", "-")
            all_exist = False
    
    console.print(table)
    return all_exist


def check_file_encoding():
    """Check for encoding issues in blockchain files"""
    files_to_check = [
        "blockchain/hash_manager.py",
        "blockchain/ipfs_storage.py",
        "blockchain/audit_trail.py"
    ]
    
    table = Table(title="📝 File Encoding Check", box=box.ROUNDED)
    table.add_column("File", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Issue", style="dim")
    
    all_clean = True
    for file_path in files_to_check:
        path = Path(file_path)
        if not path.exists():
            table.add_row(file_path, "⏭️ Skip", "File not found")
            continue
            
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                
            # Check for null bytes
            if b'\x00' in content:
                table.add_row(file_path, "❌ Error", "Contains null bytes")
                all_clean = False
                continue
            
            # Try to decode as UTF-8
            try:
                content.decode('utf-8')
                table.add_row(file_path, "✅ Clean", "UTF-8 encoded")
            except UnicodeDecodeError:
                table.add_row(file_path, "❌ Error", "Invalid UTF-8 encoding")
                all_clean = False
                
        except Exception as e:
            table.add_row(file_path, "❌ Error", str(e)[:30])
            all_clean = False
    
    console.print(table)
    return all_clean


def check_python_syntax():
    """Check if Python files have valid syntax"""
    import py_compile
    
    files_to_check = [
        "blockchain/hash_manager.py",
        "blockchain/ipfs_storage.py",
        "blockchain/audit_trail.py",
        "blockchain/digital_signature.py",
        "blockchain/merkle_tree.py",
        "blockchain/evidence_package.py"
    ]
    
    table = Table(title="🐍 Python Syntax Check", box=box.ROUNDED)
    table.add_column("File", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="dim")
    
    all_valid = True
    for file_path in files_to_check:
        path = Path(file_path)
        if not path.exists():
            table.add_row(file_path, "⏭️ Skip", "File not found")
            continue
            
        try:
            py_compile.compile(file_path, doraise=True)
            table.add_row(file_path, "✅ Valid", "Syntax OK")
        except py_compile.PyCompileError as e:
            table.add_row(file_path, "❌ Error", str(e.msg)[:40])
            all_valid = False
        except SyntaxError as e:
            table.add_row(file_path, "❌ Syntax", f"Line {e.lineno}")
            all_valid = False
    
    console.print(table)
    return all_valid


def main():
    """Run all verification checks"""
    console.print("\n[bold cyan]🔍 LandGuard Phase 5 Setup Verification[/bold cyan]\n")
    
    results = {
        "Directories": check_directories(),
        "Dependencies": check_dependencies(),
        "Config Files": check_config_files(),
        "Environment": check_env_variables(),
        "Module Files": check_blockchain_files(),
        "File Encoding": check_file_encoding(),
        "Python Syntax": check_python_syntax()
    }
    
    console.print("\n" + "="*60)
    
    # Summary
    summary_table = Table(title="📊 Setup Summary", box=box.DOUBLE)
    summary_table.add_column("Component", style="bold cyan")
    summary_table.add_column("Status", style="bold")
    
    all_passed = True
    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        summary_table.add_row(component, status)
        if not passed:
            all_passed = False
    
    console.print(summary_table)
    
    if all_passed:
        console.print("\n[bold green]🎉 All checks passed! Your Phase 5 setup is ready.[/bold green]\n")
        console.print("[yellow]Next steps:[/yellow]")
        console.print("  1. Test hash generation: python -m blockchain.hash_manager")
        console.print("  2. Test IPFS upload: python -m blockchain.ipfs_storage test_file.txt")
        console.print("  3. Run unit tests: pytest tests/test_blockchain.py -v")
        console.print("  4. Create sample evidence package")
        return 0
    else:
        console.print("\n[bold red]❌ Some checks failed. See issues above.[/bold red]\n")
        console.print("[yellow]Common fixes:[/yellow]")
        console.print("  • Null bytes: Re-save files with UTF-8 encoding")
        console.print("  • Syntax errors: Check Python code for typos")
        console.print("  • Missing files: Copy artifacts from documentation")
        console.print("  • Dependencies: pip install -r requirements_blockchain.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())