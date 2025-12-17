# LandGuard & PCC Demo Scripts

This directory contains demo scripts to showcase the capabilities of both the LandGuard document processing system and the PCC (Pied Piper Compression) system.

## Available Demo Scripts

### 1. Python Demo Script (`demo_script.py`)

A cross-platform Python script that demonstrates both systems.

**To run:**
```bash
python demo_script.py
```

### 2. PowerShell Demo Script (`demo_script.ps1`)

A Windows PowerShell script optimized for Windows environments.

**To run:**
```powershell
# In PowerShell
.\demo_script.ps1
```

## What the Demo Shows

### PCC System Features:
- File compression and encryption with AES-256-GCM
- Creation of secure .ppc container files
- File information viewing without decryption
- Secure decompression and file restoration
- IPFS integration (simulated)

### LandGuard System Features:
- AI-powered land document fraud detection
- Document risk analysis and anomaly detection
- Integration with PCC for secure document storage
- Blockchain registration simulation (Polygon)
- Audit trail generation
- Autonomous agent workflow coordination

## Prerequisites

Before running the demo scripts, ensure you have:

1. **Python 3.8+** installed
2. **Required dependencies** installed for both systems:
   ```bash
   # For PCC system
   cd pcc
   pip install -r requirements.txt
   
   # For LandGuard system
   cd landguard
   pip install -r requirements.txt
   ```

## How the Demo Works

The demo script will:

1. **Create sample documents** - Generates realistic land document samples
2. **Demonstrate PCC compression** - Shows file compression, encryption, and container creation
3. **Demonstrate LandGuard processing** - Processes documents through the complete fraud detection workflow
4. **Clean up demo files** - Removes temporary files created during the demo

## Expected Output

The demo will show:

- Command-line interface interactions
- Progress indicators for each step
- File size comparisons showing compression ratios
- Security indicators for encryption
- Fraud detection results with risk scores
- IPFS CID generation (simulated)
- Blockchain transaction simulation

## Customization

You can modify the demo scripts to:

- Use different sample documents
- Change encryption passwords
- Adjust fraud detection sensitivity
- Add more file types to test

## Troubleshooting

### Common Issues:

1. **Module not found errors:**
   - Ensure you're in the correct directory
   - Verify all dependencies are installed

2. **Permission errors:**
   - Run PowerShell as Administrator if needed
   - Ensure script execution is allowed:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```

3. **Python version issues:**
   - Verify you're using Python 3.8+
   - Check with: `python --version`

## Learning More

For detailed information about each system:

- **PCC System**: See `pcc/README.md`
- **LandGuard System**: See `landguard/README.md`
- **Technical Architecture**: See main `README.md`

## Feedback

If you encounter any issues with the demo scripts or have suggestions for improvements, please open an issue on the GitHub repository.