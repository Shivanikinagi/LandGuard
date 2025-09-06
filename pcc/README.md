# Pied Piper 2.0 — Universal AI-Powered Compression & Storage 

**Phase 1 Complete** - Advanced compression with AES-256-GCM encryption and IPFS decentralized storage.

## Features

- **AI-Powered Compression** - Intelligent compression with fallback support
- **Military-Grade Encryption** - AES-256-GCM with PBKDF2 key derivation
- **IPFS Storage** - Decentralized storage via Pinata gateway
- **Custom .ppc Format** - Metadata-rich compressed file format
- **File Type Detection** - Automatic MIME type and category detection
- **CLI Interface** - Modern Typer-based command line interface

## Installation

```bash
git clone https://github.com/Parthkk90/compression-.git
cd compression-/pcc
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

pip install typer cbor2 cryptography requests
```

## Quick Start

### Pack a File (Compress + Encrypt + Upload)
```bash
python main.py pack ../samples/test.txt --password middleout
```

**Output:**
```
 Packing: ../samples/test.txt
 Read 78 bytes
 Detected: text (text/plain)
 Compressed with: none → 78 bytes
 Encrypted
 Created: ../samples/test.txt.ppc
 Compression Ratio: 1.00x
 IPFS Link: https://gateway.pinata.cloud/ipfs/QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Unpack a File (Download + Decrypt + Decompress)
```bash
python main.py unpack ../samples/test.txt.ppc --password middleout
```

### View File Metadata
```bash
python main.py info ../samples/test.txt.ppc
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `pack` | Compress, encrypt, and upload file | `python main.py pack file.txt -p password` |
| `unpack` | Download, decrypt, and decompress file | `python main.py unpack file.ppc -p password` |
| `info` | Show metadata of .ppc file | `python main.py info file.ppc` |

## Security Features

### Encryption
- **Algorithm**: AES-256-GCM (Galois/Counter Mode)
- **Key Derivation**: PBKDF2-HMAC-SHA256 (100,000 iterations)
- **Salt**: 16-byte random salt per file
- **IV**: 12-byte random initialization vector
- **Authentication**: Built-in authentication tag

### Password Protection
- All files encrypted with user-provided password
- No password storage - derived fresh each time
- Salt prevents rainbow table attacks

## IPFS Integration

### Pinata Configuration
- **Service**: Pinata Cloud IPFS gateway
- **Upload**: Automatic upload after compression
- **Access**: Public gateway URLs for global access
- **Storage**: Permanent decentralized storage

### IPFS Links
Files uploaded to IPFS return permanent links:
```
https://gateway.pinata.cloud/ipfs/QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## .PPC File Format

Custom binary format with metadata:

```
[4 bytes: header length][JSON metadata][encrypted data]
```

### Metadata Structure
```json
{
  "original_filename": "test.txt",
  "original_mime_type": "text/plain",
  "file_type": "text",
  "model_used": "none",
  "original_size_bytes": 78,
  "compressed_size_bytes": 78,
  "compression_ratio": 1.0,
  "encryption_algo": "AES-256-GCM"
}
```

## Supported File Types

| Category | Extensions |
|----------|------------|
| **Text** | `.txt`, `.md`, `.rtf`, `.log` |
| **Images** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp` |
| **Audio** | `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.m4a` |
| **Video** | `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm` |
| **Documents** | `.pdf` |
| **Archives** | `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2` |
| **Data** | `.csv`, `.xls`, `.xlsx`, `.json`, `.xml`, `.yaml`, `.yml` |
| **Code** | `.py`, `.java`, `.cpp`, `.c`, `.js`, `.ts`, `.html`, `.css` |

## Technical Architecture

### Core Components
- **`main.py`** - CLI interface and command handlers
- **`detector/`** - File type detection system
- **`crypto/`** - AES encryption/decryption
- **`core/`** - PPC format handling
- **`storage/`** - IPFS upload client

### Fallback System
- **Null-byte resilient** - Inline fallback functions
- **AI compression** - Falls back to original data if unavailable
- **IPFS upload** - Falls back to local storage if service unavailable
- **Module imports** - Self-contained implementations prevent failures

## Compression Workflow

```
Input File → File Type Detection → AI Compression → AES Encryption → PPC Format → IPFS Upload
     ↓              ↓                    ↓              ↓             ↓           ↓
  test.txt    →   text/plain    →    original data  →  encrypted  →  .ppc    →  IPFS link
```

## Development Status

### Completed Features
- [x] CLI interface with Typer
- [x] File type detection
- [x] AES-256-GCM encryption
- [x] Custom .ppc format
- [x] IPFS integration via Pinata
- [x] Null-byte error handling
- [x] Fallback systems

### Future Enhancements
- [ ] AI compression models (VAE, BPE)
- [ ] Batch processing
- [ ] Progress bars for large files
- [ ] Compression statistics
- [ ] Web interface

## Support

For issues or questions:
- **GitHub**: [Parthkk90/compression-](https://github.com/Parthkk90/compression-)
- **Email**: parth9545kk@gmail.com

---

**Built with  by the Pied Piper team**