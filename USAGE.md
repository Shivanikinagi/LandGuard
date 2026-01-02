# 🚀 Pied Piper 2.0 - Quick Start Guide

## Installation

```powershell
# Windows (PowerShell)
cd pcc
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

```bash
# Linux/Mac
cd pcc
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Basic Usage

### 1. Pack a File (Compress + Encrypt + Package)

```bash
# Without IPFS upload (local only)
python main.py pack myfile.txt --password mySecretPassword --no-upload

# With IPFS upload (requires Pinata JWT)
python main.py pack myfile.txt --password mySecretPassword
```

### 2. View File Information

```bash
python main.py info myfile.txt.ppc
```

Output example:
```
📦 PPC File Information

File: myfile.txt.ppc
Original Name: myfile.txt
File Type: text (text/plain)
Original Size: 459 bytes
Compressed Size: 459 bytes
Compression Ratio: 1.0x (no compression)
Algorithm: none
Encryption: AES-256-GCM
Format Version: 1.0
```

### 3. Unpack a File (Decrypt + Decompress + Restore)

```bash
python main.py unpack myfile.txt.ppc --password mySecretPassword
```

This creates `restored_myfile.txt`.

### 4. Custom Output Path

```bash
# Pack with custom output
python main.py pack myfile.txt -p myPassword -o custom_name.ppc --no-upload

# Unpack with custom output
python main.py unpack custom_name.ppc -p myPassword -o original_name.txt
```

## Configuration

Create a `.env` file in the `pcc/` directory:

```env
# IPFS (Pinata) Configuration - Required for uploads
PINATA_JWT=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
PINATA_GATEWAY=https://gateway.pinata.cloud

# Optional: Model paths (if using AI compression)
VAE_MODEL_PATH=models/vae.pth
BPE_MODEL_PATH=models/bpe_tokenizer.json

# Logging
LOG_LEVEL=INFO
```

### Get Pinata JWT

1. Sign up at [pinata.cloud](https://pinata.cloud)
2. Go to API Keys
3. Create a new API key with pinning permissions
4. Copy the JWT token to `.env`

## Features

✅ **Working Now:**
- ✅ File encryption (AES-256-GCM)
- ✅ Custom .ppc container format
- ✅ Pack/unpack files
- ✅ View file info without extracting
- ✅ IPFS upload support (when configured)

🔄 **Future Phases:**
- AI-powered compression (VAE for images, BPE for text)
- Blockchain integration
- Smart contracts for file verification
- Advanced compression algorithms

## Command Reference

| Command | Description |
|---------|-------------|
| `pack` | Compress, encrypt, and package a file |
| `unpack` | Decrypt and restore a .ppc file |
| `info` | Display file metadata without extracting |
| `version` | Show version information |

## Common Options

| Option | Short | Description |
|--------|-------|-------------|
| `--password` | `-p` | Encryption/decryption password |
| `--output` | `-o` | Custom output file path |
| `--upload/--no-upload` | - | Enable/disable IPFS upload (default: upload) |
| `--help` | - | Show help message |

## Examples

### Secure File Storage

```bash
# Encrypt sensitive document
python main.py pack confidential.pdf -p SecurePassword123 --no-upload

# Later, decrypt it
python main.py unpack confidential.pdf.ppc -p SecurePassword123
```

### IPFS Sharing

```bash
# Upload to IPFS and share the link
python main.py pack presentation.pptx -p SharePassword

# Output includes IPFS link:
# 🌐 IPFS Link: https://gateway.pinata.cloud/ipfs/Qm...
```

### Batch Processing

```powershell
# Windows PowerShell - Pack all text files
Get-ChildItem *.txt | ForEach-Object {
    python main.py pack $_.Name -p BatchPassword --no-upload
}
```

```bash
# Linux/Mac - Pack all text files
for file in *.txt; do
    python main.py pack "$file" -p BatchPassword --no-upload
done
```

## Troubleshooting

### "ModuleNotFoundError"
```bash
# Make sure virtual environment is activated and dependencies installed
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### "IPFS upload failed"
- Make sure `PINATA_JWT` is set in `.env`
- Or use `--no-upload` to skip IPFS

### "Incorrect password"
- Password is case-sensitive
- Make sure you're using the same password for pack and unpack

## Security Notes

⚠️ **Important:**
- Store passwords securely - lost passwords cannot be recovered
- `.ppc` files use AES-256-GCM encryption (military-grade)
- Original files are never uploaded unencrypted to IPFS
- Keep your `.env` file secure (it's gitignored by default)

## Next Steps

1. ✅ Test with your files
2. ⏭️ Deploy blockchain contracts (see [BLOCKCHAIN_DEPLOYMENT.md](BLOCKCHAIN_DEPLOYMENT.md))
3. ⏭️ Set up LandGuard AI agents
4. ⏭️ Explore Docker deployment

For full deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).
