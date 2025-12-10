# 🚀 Pied Piper 2.0 — Universal AI-Powered Compression & Storage

> **Advanced file compression with military-grade encryption and decentralized storage**

**Phase 1 Complete** ✅ - Production-ready compression system with AES-256-GCM encryption and IPFS integration.

---

## 🌟 What is Pied Piper 2.0?

Pied Piper 2.0 is an intelligent file compression system that:
- 🤖 **Compresses** your files using AI-powered algorithms
- 🔒 **Encrypts** them with military-grade AES-256-GCM encryption
- 🌐 **Stores** them on the decentralized IPFS network
- 📦 **Packages** everything in a custom `.ppc` container format

Perfect for secure file storage, sharing, and archiving!

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI-Powered Compression** | Intelligent compression with automatic fallback |
| 🔐 **Military-Grade Encryption** | AES-256-GCM with PBKDF2 key derivation |
| 🌐 **IPFS Decentralized Storage** | Permanent storage via Pinata gateway |
| 📦 **Custom .ppc Format** | Metadata-rich container format |
| 🎯 **Smart File Detection** | Automatic MIME type and category recognition |
| 💻 **Modern CLI Interface** | Easy-to-use command line tool |

---

## 📋 Prerequisites

Before installing, make sure you have:
- **Python 3.8+** installed ([Download here](https://www.python.org/downloads/))
- **Git** installed ([Download here](https://git-scm.com/downloads))
- **Basic command line knowledge**

---

## 🚀 Installation Guide

### Step 1: Clone the Repository
```bash
git clone https://github.com/Parthkk90/compression-.git
cd compression-
```

### Step 2: Navigate to the Project Directory
```bash
cd pcc
```

### Step 3: Create Virtual Environment
```bash
python -m venv venv
```

### Step 4: Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
.\venv\Scripts\activate.bat
```

**On Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 5: Install Dependencies
```bash
pip install typer cbor2 cryptography requests rich
```

### Step 6: Verify Installation
```bash
python main.py --help
```

You should see the help menu with available commands!

---

## 📖 Quick Start Guide

### 🎯 Example 1: Compress Your First File

**Step 1:** Create a test file
```bash
echo "Hello, Pied Piper!" > test.txt
```

**Step 2:** Compress and encrypt it
```bash
python main.py pack test.txt --password mySecurePassword123
```

**What happens:**
- ✅ File is compressed
- ✅ Encrypted with your password
- ✅ Uploaded to IPFS
- ✅ Saved as `test.txt.ppc`

**Expected Output:**
```
✅ Packing: test.txt
📊 Read 20 bytes
🔍 Detected: text (text/plain)
📦 Compressed with: huffman → 15 bytes
🔒 Encrypted with AES-256-GCM
💾 Created: test.txt.ppc
📈 Compression Ratio: 1.33x (25% smaller)
🌐 IPFS Link: https://gateway.pinata.cloud/ipfs/Qm...
```

---

### 🔓 Example 2: Decompress Your File

**Restore the original file:**
```bash
python main.py unpack test.txt.ppc --password mySecurePassword123
```

**What happens:**
- ✅ File is decrypted with your password
- ✅ Decompressed to original format
- ✅ Saved as `restored_test.txt`

**Expected Output:**
```
🔓 Unpacking: test.txt.ppc
🔑 Decrypted successfully
📤 Decompressed: 15 → 20 bytes
💾 Restored: restored_test.txt
```

---

### 📊 Example 3: View File Information

**Check metadata without extracting:**
```bash
python main.py info test.txt.ppc
```

**Output shows:**
- Original filename and size
- Compression algorithm used
- Compression ratio achieved
- Encryption details
- File type information

---

## 📚 Command Reference

### Main Commands

| Command | Purpose | Usage |
|---------|---------|-------|
| `pack` | Compress, encrypt & upload file | `python main.py pack <file> -p <password>` |
| `unpack` | Decrypt & decompress file | `python main.py unpack <file.ppc> -p <password>` |
| `info` | Display file metadata | `python main.py info <file.ppc>` |

### Command Options

**Pack Command:**
```bash
python main.py pack <input_file> --password <your_password>
```
- `<input_file>`: Path to the file you want to compress
- `--password` or `-p`: Password for encryption (required)

**Unpack Command:**
```bash
python main.py unpack <ppc_file> --password <your_password> [--output <output_path>]
```
- `<ppc_file>`: Path to the .ppc file
- `--password` or `-p`: Password used during compression
- `--output` or `-o`: (Optional) Custom output filename

**Info Command:**
```bash
python main.py info <ppc_file>
```
- No password needed - only reads metadata

---

## 🔐 Security Features

### Encryption Details

| Feature | Specification |
|---------|--------------|
| **Algorithm** | AES-256-GCM (Galois/Counter Mode) |
| **Key Derivation** | PBKDF2-HMAC-SHA256 |
| **Iterations** | 100,000 (slows down brute-force attacks) |
| **Salt** | 16-byte random per file |
| **IV** | 12-byte random per file |
| **Authentication** | Built-in authentication tag |

### Why This is Secure

✅ **Military-Grade Encryption** - Same standard used by governments  
✅ **Unique Salt Per File** - Prevents rainbow table attacks  
✅ **Authentication Tag** - Detects tampering attempts  
✅ **No Password Storage** - Password never saved anywhere  
✅ **Key Stretching** - PBKDF2 makes cracking extremely slow

### Blockchain Verification

✅ **Immutable Records** - All documents registered on Polygon Mumbai testnet  
✅ **Transparent Verification** - Transactions visible on [PolygonScan Explorer](https://mumbai.polygonscan.com/)  
✅ **Decentralized Storage** - IPFS ensures permanent document availability  
✅ **Tamper-Evident** - Any modification breaks the cryptographic chain

---

## 🌐 IPFS Integration

### What is IPFS?

IPFS (InterPlanetary File System) is a decentralized storage network that:
- 🌍 Stores files across multiple nodes worldwide
- 🔗 Provides permanent content-addressed links
- 🚀 Enables fast peer-to-peer file sharing
- 💪 Resists censorship and single points of failure

### How It Works

1. **Upload**: Your encrypted `.ppc` file is uploaded to Pinata's IPFS gateway
2. **CID Generation**: Receives unique Content Identifier (CID)
3. **Global Access**: Anyone with the link can download your file
4. **Permanent Storage**: File remains accessible as long as it's pinned

### IPFS Link Format
```
https://gateway.pinata.cloud/ipfs/QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Note:** Files are encrypted before upload, so only those with your password can decrypt them!

---

## 📦 Understanding the .PPC Format

### What is a .ppc File?

`.ppc` files are custom containers created by Pied Piper that bundle:
- 📋 **Metadata** (file info, compression details)
- 🔒 **Encrypted Data** (your compressed content)

### File Structure
```
┌─────────────────────────────────────┐
│  Header (4 bytes)                   │  ← Size of metadata
├─────────────────────────────────────┤
│  Metadata (JSON)                    │  ← File information
├─────────────────────────────────────┤
│  Encrypted Compressed Data          │  ← Your protected content
└─────────────────────────────────────┘
```

### Metadata Contents
```json
{
  "original_filename": "document.pdf",
  "original_mime_type": "application/pdf",
  "file_type": "document",
  "model_used": "huffman",
  "original_size_bytes": 1048576,
  "compressed_size_bytes": 524288,
  "compression_ratio": 2.0,
  "encryption_algo": "AES-256-GCM",
  "created_at": "2025-11-24T10:30:00Z"
}
```

**Why This Matters:**
- ✅ Self-documenting files
- ✅ Easy to verify compression effectiveness
- ✅ Tracks which algorithm was used
- ✅ Preserves original file information

---

## 📁 Supported File Types

Pied Piper 2.0 intelligently handles various file types:

| Category | File Extensions | Compression Method |
|----------|----------------|-------------------|
| 📝 **Text** | `.txt`, `.md`, `.rtf`, `.log`, `.csv` | Huffman Coding |
| 🖼️ **Images** | `.jpg`, `.png`, `.gif`, `.bmp`, `.webp` | VAE (Neural Network) |
| 🎵 **Audio** | `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg` | Placeholder (Coming Soon) |
| 🎥 **Video** | `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm` | Placeholder (Coming Soon) |
| 📄 **Documents** | `.pdf`, `.docx`, `.xlsx`, `.pptx` | Smart Detection |
| 🗜️ **Archives** | `.zip`, `.rar`, `.7z`, `.tar`, `.gz` | Pass-through |
| 📊 **Data** | `.json`, `.xml`, `.yaml`, `.sql` | Huffman Coding |
| 💻 **Code** | `.py`, `.java`, `.js`, `.cpp`, `.html` | Huffman Coding |

**Note:** If AI compression fails or is unavailable, the system automatically falls back to standard compression methods!

---

## 🔧 How It Works

### Complete Workflow

```
┌──────────────┐
│  Input File  │
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│ 🔍 File Type        │  Detect MIME type and category
│    Detection        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ 🤖 AI Compression   │  Apply intelligent compression
│                     │  (Huffman, VAE, etc.)
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ 🔒 AES Encryption   │  Encrypt with your password
│                     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ 📦 PPC Packaging    │  Create .ppc container
│                     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ 🌐 IPFS Upload      │  Upload to decentralized network
│                     │
└──────┬──────────────┘
       │
       ▼
┌──────────────────┐
│  🎉 Done!        │  File compressed, encrypted & uploaded
└──────────────────┘
```

### Decompression Workflow

```
.ppc File → Decrypt → Decompress → Restore Original File
```

---

## 💡 Usage Examples

### Example 1: Secure Document Storage
```bash
# Compress and encrypt a confidential document
python main.py pack confidential.pdf -p MyStr0ngP@ssw0rd

# Share the IPFS link with authorized users
# They can download and decrypt with the password
python main.py unpack confidential.pdf.ppc -p MyStr0ngP@ssw0rd
```

### Example 2: Batch Processing Multiple Files
```bash
# Compress multiple files with the same password
python main.py pack report1.txt -p project2024
python main.py pack report2.txt -p project2024
python main.py pack report3.txt -p project2024
```

### Example 3: Code Backup
```bash
# Backup your source code securely
python main.py pack main.py -p backup123
python main.py pack config.json -p backup123

# Later, restore them
python main.py unpack main.py.ppc -p backup123
python main.py unpack config.json.ppc -p backup123
```

### Example 4: Check File Details
```bash
# View metadata without extracting
python main.py info document.pdf.ppc

# Check compression effectiveness
# Look for "compression_ratio" in the output
```

---

## 🎓 Tips & Best Practices

### Password Security
✅ **DO:**
- Use strong passwords (12+ characters)
- Mix uppercase, lowercase, numbers, symbols
- Use unique passwords for important files
- Store passwords in a password manager

❌ **DON'T:**
- Use common words or phrases
- Reuse passwords from other services
- Share passwords over insecure channels
- Forget your password (files cannot be recovered!)

### File Management
✅ **DO:**
- Keep original files until you verify .ppc extraction works
- Test decompression immediately after compression
- Store IPFS links in a safe place
- Use descriptive filenames

❌ **DON'T:**
- Delete original files without testing
- Compress already compressed files (ZIP, RAR, etc.)
- Use very weak passwords for sensitive data

### Performance Tips
💡 **Large Files:** Processing may take longer (1-2 minutes for 100MB+)  
💡 **Already Compressed:** ZIP, PNG, MP4 won't compress much further  
💡 **Text Files:** Achieve best compression ratios (up to 50-70%)  
💡 **Network Speed:** IPFS upload speed depends on your internet connection

---

## 🏗️ Technical Architecture

### System Components

```
pcc/
├── main.py                 # 🎯 CLI entry point and command handlers
├── cli/
│   └── main.py            # 💻 Interactive menu interface
├── core/
│   └── ppc_format.py      # 📦 PPC container format logic
├── detector/
│   └── file_type.py       # 🔍 MIME type and category detection
├── crypto/
│   └── aes.py             # 🔒 AES-256-GCM encryption/decryption
├── storage/
│   └── ipfs_client.py     # 🌐 IPFS upload via Pinata
├── models/
│   ├── registry.py        # 🗂️ Model selection system
│   ├── text_huffman.py    # 📝 Huffman compression for text
│   ├── image_vae.py       # 🖼️ VAE compression for images
│   └── base.py            # 🏗️ Base compression interface
└── compressors/
    ├── image/
    │   ├── train_vae.py   # 🎓 VAE model training
    │   └── vae.py         # 🧠 Neural network architecture
    └── text/
        └── bpe_compressor.py  # 📊 Byte Pair Encoding
```

### How Components Work Together

1. **CLI Layer** (`main.py`, `cli/main.py`)
   - Handles user input and commands
   - Provides interactive menu interface
   - Displays progress and results

2. **Detection Layer** (`detector/`)
   - Identifies file MIME type
   - Categorizes file (text, image, video, etc.)
   - Selects appropriate compression model

3. **Compression Layer** (`models/`, `compressors/`)
   - Applies AI-powered compression
   - Falls back to standard algorithms if needed
   - Tracks compression ratios

4. **Security Layer** (`crypto/`)
   - Generates secure encryption keys from passwords
   - Encrypts compressed data with AES-256-GCM
   - Adds authentication tags

5. **Packaging Layer** (`core/`)
   - Creates .ppc container format
   - Embeds metadata (file info, compression stats)
   - Ensures cross-platform compatibility

6. **Storage Layer** (`storage/`)
   - Uploads to IPFS via Pinata gateway
   - Returns permanent content-addressed links
   - Handles upload failures gracefully

### Intelligent Fallback System

The system has multiple fallback layers to ensure reliability:

```
AI Compression Attempt
    ↓
[Success?] ─Yes→ Use AI-compressed data
    ↓
   No
    ↓
Standard Compression (Zstd/Brotli)
    ↓
[Success?] ─Yes→ Use standard-compressed data
    ↓
   No
    ↓
Store Original Data (no compression)
```

**This ensures:**
- ✅ No file corruption or data loss
- ✅ System works even if AI models unavailable
- ✅ Graceful degradation of features
- ✅ Always produces valid .ppc files

---

## 🔬 Compression Algorithms

### 1. Huffman Coding (Text Files)

**How it works:**
- Analyzes character frequency in your text
- Assigns shorter codes to common characters
- Assigns longer codes to rare characters
- Achieves 30-50% size reduction for typical text

**Best for:** `.txt`, `.md`, `.log`, `.csv`, `.json`, `.xml`, code files

**Example:**
```
Original:  "AAABBC" (48 bits with 8-bit encoding)
Huffman:   A=0, B=10, C=11 → "00010101011" (11 bits)
Savings:   77% compression!
```

### 2. VAE (Variational Auto-Encoder) for Images

**How it works:**
- Neural network trained on 13,420 CIFAR-10 images
- Encodes images into compact latent space representation
- Learns to preserve important visual features
- Achieves lossy compression with quality control

**Best for:** `.jpg`, `.png`, `.bmp`, `.gif` (photos and graphics)

**Example:**
```
Original:  256×256 RGB image (196,608 bytes)
VAE:       Compressed latent vector (~2,000 bytes)
Savings:   98% compression with acceptable quality
```

### 3. Future: Video Compression

**Planned implementation:**
- Neural Video Codec (NVC)
- Frame-by-frame VAE encoding
- Temporal compression between frames
- Target: 50-70% size reduction vs H.264

---

## 📊 Development Status

### ✅ Phase 1: Core System (COMPLETE)

| Feature | Status | Notes |
|---------|--------|-------|
| CLI Interface | ✅ Complete | Typer-based with rich output |
| File Type Detection | ✅ Complete | MIME type and category detection |
| AES-256-GCM Encryption | ✅ Complete | Military-grade security |
| PPC Container Format | ✅ Complete | Metadata-rich packaging |
| IPFS Integration | ✅ Complete | Pinata gateway upload |
| Huffman Text Compression | ✅ Complete | 30-50% text compression |
| VAE Image Compression | ⚠️ Partial | Model trained, debugging in progress |
| Error Handling | ✅ Complete | Comprehensive fallback system |

### 🚧 Phase 2: Enhancement (IN PROGRESS)

| Feature | Status | Target |
|---------|--------|--------|
| Video Compression | 🔄 Planned | Neural Video Codec |
| Audio Compression | 🔄 Planned | Wavelet-based compression |
| Image Decompression Fix | 🐛 Debugging | Resolve 0-byte output issue |
| Batch Processing | 📋 Planned | Process multiple files at once |
| Progress Bars | 📋 Planned | Visual feedback for large files |
| Web Interface | 💡 Future | Browser-based UI |

### 🔮 Phase 3: Advanced Features (PLANNED)

- [ ] Custom model training interface
- [ ] Compression quality presets (fast/balanced/maximum)
- [ ] Deduplication for similar files
- [ ] Compression statistics dashboard
- [ ] API for programmatic access
- [ ] Docker containerization
- [ ] Cloud deployment options

---

## ❓ Troubleshooting

### Common Issues and Solutions

#### 1. "Module not found" Error
**Problem:** Python can't find required packages

**Solution:**
```bash
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. "Decryption failed" Error
**Problem:** Wrong password or corrupted file

**Solution:**
- ✅ Verify you're using the correct password (case-sensitive!)
- ✅ Check if the .ppc file is corrupted (try downloading again)
- ✅ Ensure file wasn't modified after creation

#### 3. IPFS Upload Fails
**Problem:** Network issues or Pinata service unavailable

**Solution:**
- ✅ Check your internet connection
- ✅ File is still saved locally (in same folder as input)
- ✅ You can manually upload the .ppc file to IPFS later

#### 4. Low Compression Ratio
**Problem:** File doesn't compress well (ratio close to 1.0)

**Solution:**
- This is normal for already-compressed files (ZIP, MP4, PNG)
- These formats are already optimized
- Encryption still protects your data

#### 5. Python Version Issues
**Problem:** "SyntaxError" or compatibility issues

**Solution:**
```bash
# Check your Python version
python --version

# Should be 3.8 or higher
# If not, upgrade Python and recreate virtual environment
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

1. **Report Bugs** 🐛
   - Open an issue on GitHub
   - Include error messages and steps to reproduce

2. **Suggest Features** 💡
   - Share ideas for new compression algorithms
   - Propose UI/UX improvements

3. **Submit Code** 💻
   - Fork the repository
   - Create a feature branch
   - Submit a pull request

4. **Improve Documentation** 📚
   - Fix typos or unclear instructions
   - Add examples and tutorials
   - Translate documentation

### Development Setup
```bash
# Clone repository
git clone https://github.com/Parthkk90/compression-.git
cd compression-/pcc

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black .
```

---

## 📞 Support & Contact

### Need Help?

- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/Parthkk90/compression-/issues)
- 💬 **Questions:** [GitHub Discussions](https://github.com/Parthkk90/compression-/discussions)
- 📧 **Email:** parth9545kk@gmail.com
- 🌐 **Website:** [Coming Soon]

### Response Time
- Critical bugs: 24-48 hours
- Feature requests: 1-2 weeks
- General questions: 2-3 days

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**What this means:**
- ✅ Free to use for personal and commercial projects
- ✅ Modify and distribute as you wish
- ✅ No warranty provided (use at your own risk)

---

## 🙏 Acknowledgments

Special thanks to:
- **OpenAI** - For GPT and compression research inspiration
- **IPFS Community** - For decentralized storage technology
- **Pinata** - For IPFS gateway services
- **PyTorch Team** - For deep learning framework
- **Typer** - For excellent CLI framework

### Research References
- Huffman, D. A. (1952). "A Method for the Construction of Minimum-Redundancy Codes"
- Kingma, D. P., & Welling, M. (2014). "Auto-Encoding Variational Bayes"
- Ballé, J., et al. (2018). "Variational Image Compression with a Scale Hyperprior"

---

## 🎯 Project Roadmap

### Q1 2025
- ✅ Core compression system
- ✅ AES encryption integration
- ✅ IPFS storage support
- ✅ CLI interface

### Q2 2025
- 🔄 Fix image decompression bug
- 🔄 Implement video compression
- 🔄 Add audio compression
- 🔄 Web interface prototype

### Q3 2025
- 📋 Batch processing
- 📋 Compression quality presets
- 📋 API development
- 📋 Docker support

### Q4 2025
- 💡 Cloud deployment
- 💡 Mobile app
- 💡 Enterprise features
- 💡 Performance optimization

---

<div align="center">

## ⭐ Star This Project!

If you find Pied Piper 2.0 useful, please give it a star on GitHub!

**Built with ❤️ by the Pied Piper Team**

*Making the world a more compressed place, one file at a time.*

---

**Version:** 2.0.0 | **Last Updated:** November 2025

</div>
