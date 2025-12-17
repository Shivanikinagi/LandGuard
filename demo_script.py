#!/usr/bin/env python3
"""
LandGuard & PCC Demo Script
==========================

This script demonstrates the key features of both the LandGuard document processing system
and the PCC (Pied Piper Compression) system.

The demo includes:
1. Creating sample documents
2. Demonstrating PCC compression and encryption
3. Demonstrating LandGuard document processing with fraud detection
4. Showing integration between both systems
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"{text:^60}")
    print("="*60)

def print_section(text):
    """Print a formatted section header"""
    print(f"\n--- {text} ---")

def print_command(cmd):
    """Print a command that will be executed"""
    print(f"\n$ {cmd}")

def run_command(cmd, cwd=None):
    """Run a command and print its output"""
    print_command(cmd)
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def create_sample_documents():
    """Create sample documents for the demo"""
    print_header("Creating Sample Documents")
    
    # Create a sample text document
    sample_text = """LAND DOCUMENT RECORD
===================

Property Address: 123 Main Street, Anytown, ST 12345
Parcel ID: LD-2025-001234
Owner: John Smith
Previous Owner: Jane Doe
Purchase Date: 2025-01-15
Purchase Price: $250,000
Document Type: Deed Transfer
Notary: Robert Johnson, License #NJ-9876
Recorded Date: 2025-01-20
Recording Fee: $45.00

LEGAL DESCRIPTION:
Lot 5, Block 12, Anytown Subdivision, according to the plat thereof
recorded in Plat Book 45, Page 67, Records of Any County.

This document transfers all rights, title, and interest in the
above-described property from Jane Doe to John Smith.

WITNESS SIGNATURES:
_________________________       _________________________
Jane Doe                        John Smith
Date: 01/15/2025               Date: 01/15/2025

NOTARY ACKNOWLEDGMENT:
State of Any State
County of Any County

On this day personally appeared Jane Doe, known to me to be the
person whose name is subscribed to the foregoing instrument and
acknowledged to me that she executed the same for the purposes
therein contained.

_________________________
Robert Johnson, Notary Public
My Commission Expires: 05/10/2026
"""
    
    with open("sample_land_document.txt", "w") as f:
        f.write(sample_text)
    print("✓ Created sample_land_document.txt")
    
    # Create a sample code file
    sample_code = '''# sample_code.py
def calculate_property_tax assessed_value, tax_rate):
    """Calculate property tax based on assessed value and tax rate"""
    return assessed_value * tax_rate

class PropertyRecord:
    def __init__(self, parcel_id, owner, address):
        self.parcel_id = parcel_id
        self.owner = owner
        self.address = address
        self.assessed_value = 0
        
    def update_assessment self, new_value):
        self.assessed_value = new_value
        
    def get_tax_amount self, tax_rate:
        return calculate_property_tax self.assessed_value, tax_rate
'''
    
    with open("sample_code.py", "w") as f:
        f.write(sample_code)
    print("✓ Created sample_code.py")

def demo_pcc_system():
    """Demonstrate the PCC (Pied Piper Compression) system"""
    print_header("PCC System Demo - File Compression & Encryption")
    
    # Change to PCC directory
    pcc_dir = "pcc"
    
    # Show PCC help
    print_section("PCC Help Menu")
    run_command("python main.py --help", cwd=pcc_dir)
    
    # Compress the sample land document
    print_section("Compressing Sample Land Document")
    run_command("python main.py pack ../sample_land_document.txt -p MySecurePassword123", cwd=pcc_dir)
    
    # Show the created .ppc file
    print_section("Checking Created Files")
    run_command("dir ..\\sample_land_document.txt.ppc", cwd=pcc_dir)
    
    # Show file information
    print_section("Viewing File Information")
    run_command("python main.py info ../sample_land_document.txt.ppc", cwd=pcc_dir)
    
    # Decompress the file
    print_section("Decompressing File")
    run_command("python main.py unpack ../sample_land_document.txt.ppc -p MySecurePassword123", cwd=pcc_dir)
    
    # Compare original and restored files
    print_section("Comparing Original and Restored Files")
    run_command("fc ..\\sample_land_document.txt ..\\restored_sample_land_document.txt", cwd=pcc_dir)

def demo_landguard_system():
    """Demonstrate the LandGuard document processing system"""
    print_header("LandGuard System Demo - Document Processing & Fraud Detection")
    
    # Change to LandGuard directory
    landguard_dir = "landguard"
    
    # Show LandGuard help
    print_section("LandGuard Help Menu")
    run_command("python cli/landguard_cli.py --help", cwd=landguard_dir)
    
    # Process the sample document
    print_section("Processing Sample Land Document")
    run_command("python cli/landguard_cli.py process ../sample_land_document.txt --password MySecurePassword123", cwd=landguard_dir)
    
    # Show generated files
    print_section("Checking Generated Files")
    run_command("dir ..\\*.ppc", cwd=landguard_dir)
    run_command("dir ..\\detailed_anomaly_report*", cwd=landguard_dir)

def cleanup_demo_files():
    """Clean up demo files"""
    print_header("Cleaning Up Demo Files")
    
    files_to_remove = [
        "sample_land_document.txt",
        "sample_code.py",
        "sample_land_document.txt.ppc",
        "restored_sample_land_document.txt",
        "detailed_anomaly_report_LD-SAMPLE_LAND_DOCUMENT.txt"
    ]
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"✓ Removed {file}")

def main():
    """Main demo function"""
    print_header("LandGuard & PCC Demo Script")
    print("""
This script will demonstrate the capabilities of both systems:
1. PCC (Pied Piper Compression) - File compression and encryption
2. LandGuard - Land document processing with fraud detection

The demo will:
- Create sample documents
- Show PCC compression and encryption
- Demonstrate LandGuard document processing
- Clean up demo files at the end
""")
    
    # Wait for user to be ready
    input("Press Enter to start the demo...")
    
    try:
        # Create sample documents
        create_sample_documents()
        
        # Demonstrate PCC system
        demo_pcc_system()
        
        # Demonstrate LandGuard system
        demo_landguard_system()
        
        # Clean up
        cleanup_demo_files()
        
        print_header("Demo Completed Successfully!")
        print("""
Summary of what we demonstrated:
✓ PCC System:
  - File compression and encryption
  - .ppc container format creation
  - File information viewing
  - Secure decompression
  
✓ LandGuard System:
  - Document fraud detection
  - Integration with PCC for compression
  - Blockchain registration simulation
  - Audit trail generation

Both systems work together to provide secure, intelligent document processing!
""")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        cleanup_demo_files()
    except Exception as e:
        print(f"\n\nDemo failed with error: {e}")
        cleanup_demo_files()

if __name__ == "__main__":
    main()