# Pied Piper 2.0 — Universal AI-Powered Compression & Storage

## Features
- AI-powered compression (VQVAE for images, Huffman for text)
- Military-grade AES-256-GCM encryption
- Custom `.ppc` container format with metadata
- Automatic file type detection and model selection
- Interactive and command-line interface

## Installation

```bash
git clone https://github.com/Parthkk90/compression-.git
cd compression-/pcc
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Interactive CLI
```bash
python -m pcc.cli.main
```
- Follow prompts to compress or decompress files.

### Direct CLI Commands
```bash
python -m pcc.cli.main compress pcc/samples/test.txt secret --model text-huffman
python -m pcc.cli.main decompress pcc/samples/test.txt.ppc secret --output restored.txt
```

## Supported File Types
- Text: `.txt`, `.md`, `.csv`
- Images: `.png`, `.jpg`, `.jpeg`, `.bmp`
- Video: `.mp4`, `.avi`
- Audio: `.mp3`, `.wav`
- Archives: `.zip`, `.tar`
- More...

## Project Structure

```
pcc/
  cli/main.py         # Main CLI entry point
  models/             # Compression models (VAE, Huffman, etc.)
  compressors/        # Model implementations
  core/ppc_format.py  # PPC container format
  crypto/aes.py       # Encryption logic
  samples/            # Sample files for testing
```

## Troubleshooting

- If image compression ratio is 0%, check that `vae_model.pth` exists in `pcc/compressors/image/models/`.
- For best results, use uncompressed files (BMP, WAV, CSV).
- For already compressed files (PNG, MP4, ZIP), fallback will store raw or Zstd-compressed data.

## License
MIT

---

**Built by Parth KK, Ansh G., & Neel S.**