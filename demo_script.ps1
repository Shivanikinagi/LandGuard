# LandGuard & PCC Demo Script for Windows PowerShell
# ==================================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "     LandGuard & PCC Demo Script           " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

Write-Host @"
This script will demonstrate the capabilities of both systems:
1. PCC (Pied Piper Compression) - File compression and encryption
2. LandGuard - Land document processing with fraud detection

The demo will:
- Create sample documents
- Show PCC compression and encryption
- Demonstrate LandGuard document processing
- Clean up demo files at the end
"@ -ForegroundColor Yellow

Write-Host ""
Write-Host "Press any key to start the demo..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

function Create-SampleDocuments {
    Write-Host "`n--- Creating Sample Documents ---" -ForegroundColor Magenta
    
    # Create a sample text document
    $sampleText = @"
LAND DOCUMENT RECORD
===================

Property Address: 123 Main Street, Anytown, ST 12345
Parcel ID: LD-2025-001234
Owner: John Smith
Previous Owner: Jane Doe
Purchase Date: 2025-01-15
Purchase Price: `$250,000
Document Type: Deed Transfer
Notary: Robert Johnson, License #NJ-9876
Recorded Date: 2025-01-20
Recording Fee: `$45.00

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
"@

    Set-Content -Path "sample_land_document.txt" -Value $sampleText
    Write-Host "✓ Created sample_land_document.txt" -ForegroundColor Green
    
    # Create a sample code file
    $sampleCode = @'
# sample_code.py
def calculate_property_tax(assessed_value, tax_rate):
    """Calculate property tax based on assessed value and tax rate"""
    return assessed_value * tax_rate

class PropertyRecord:
    def __init__(self, parcel_id, owner, address):
        self.parcel_id = parcel_id
        self.owner = owner
        self.address = address
        self.assessed_value = 0
        
    def update_assessment(self, new_value):
        self.assessed_value = new_value
        
    def get_tax_amount(self, tax_rate):
        return calculate_property_tax(self.assessed_value, tax_rate)
'@

    Set-Content -Path "sample_code.py" -Value $sampleCode
    Write-Host "✓ Created sample_code.py" -ForegroundColor Green
}

function Demo-PCCSystem {
    Write-Host "`n============================================" -ForegroundColor Cyan
    Write-Host "     PCC System Demo - File Compression     " -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    
    # Show PCC help
    Write-Host "`n--- PCC Help Menu ---" -ForegroundColor Magenta
    Set-Location -Path "pcc"
    python main.py --help
    
    # Compress the sample land document
    Write-Host "`n--- Compressing Sample Land Document ---" -ForegroundColor Magenta
    python main.py pack ../sample_land_document.txt -p MySecurePassword123
    
    # Show the created .ppc file
    Write-Host "`n--- Checking Created Files ---" -ForegroundColor Magenta
    Get-ChildItem -Path "..\sample_land_document.txt.ppc" | Format-Table Name, Length, LastWriteTime
    
    # Show file information
    Write-Host "`n--- Viewing File Information ---" -ForegroundColor Magenta
    python main.py info ../sample_land_document.txt.ppc
    
    # Decompress the file
    Write-Host "`n--- Decompressing File ---" -ForegroundColor Magenta
    python main.py unpack ../sample_land_document.txt.ppc -p MySecurePassword123
    
    # Compare original and restored files
    Write-Host "`n--- Comparing Original and Restored Files ---" -ForegroundColor Magenta
    $diff = Compare-Object (Get-Content "..\sample_land_document.txt") (Get-Content "..\restored_sample_land_document.txt")
    if ($null -eq $diff) {
        Write-Host "✓ Files are identical" -ForegroundColor Green
    } else {
        Write-Host "✗ Files differ" -ForegroundColor Red
        $diff
    }
    
    Set-Location -Path ".."
}

function Demo-LandGuardSystem {
    Write-Host "`n============================================" -ForegroundColor Cyan
    Write-Host "   LandGuard System Demo - Document Processing " -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    
    # Show LandGuard help
    Write-Host "`n--- LandGuard Help Menu ---" -ForegroundColor Magenta
    Set-Location -Path "landguard"
    python cli/landguard_cli.py --help
    
    # Process the sample document
    Write-Host "`n--- Processing Sample Land Document ---" -ForegroundColor Magenta
    python cli/landguard_cli.py process ../sample_land_document.txt --password MySecurePassword123
    
    # Show generated files
    Write-Host "`n--- Checking Generated Files ---" -ForegroundColor Magenta
    Get-ChildItem -Path "..\*.ppc" -ErrorAction SilentlyContinue | Format-Table Name, Length, LastWriteTime
    Get-ChildItem -Path "..\detailed_anomaly_report*" -ErrorAction SilentlyContinue | Format-Table Name, Length, LastWriteTime
    
    Set-Location -Path ".."
}

function Cleanup-DemoFiles {
    Write-Host "`n--- Cleaning Up Demo Files ---" -ForegroundColor Magenta
    
    $filesToRemove = @(
        "sample_land_document.txt",
        "sample_code.py",
        "sample_land_document.txt.ppc",
        "restored_sample_land_document.txt",
        "detailed_anomaly_report_LD-SAMPLE_LAND_DOCUMENT.txt"
    )
    
    foreach ($file in $filesToRemove) {
        if (Test-Path $file) {
            Remove-Item $file -Force
            Write-Host "✓ Removed $file" -ForegroundColor Green
        }
    }
}

try {
    # Create sample documents
    Create-SampleDocuments
    
    # Demonstrate PCC system
    Demo-PCCSystem
    
    # Demonstrate LandGuard system
    Demo-LandGuardSystem
    
    # Clean up
    Cleanup-DemoFiles
    
    Write-Host "`n============================================" -ForegroundColor Cyan
    Write-Host "        Demo Completed Successfully!        " -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    
    Write-Host @"
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
"@ -ForegroundColor Yellow
    
} catch {
    Write-Host "`nDemo failed with error: $($_.Exception.Message)" -ForegroundColor Red
    Cleanup-DemoFiles
}

Write-Host "`nPress any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")