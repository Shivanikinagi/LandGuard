"""
Pied Piper 2.0 - FastAPI Web Service
Public API for file compression and encryption
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add PCC to path
pcc_path = os.path.join(os.path.dirname(__file__), "..", "pcc")
sys.path.insert(0, pcc_path)

from compressors.compressor import compress_file
from compressors.decompressor import decompress_file
from crypto.aes import encrypt_data, decrypt_data
from storage.ipfs_client import upload_to_ipfs
from core.ppc_format import create_ppc_file, PPCFile
from detector.file_type import detect_file_type

app = FastAPI(
    title="Pied Piper 2.0 API",
    description="Advanced file compression with encryption and IPFS storage",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def root():
    """Serve the main web interface"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": "Pied Piper 2.0 API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}


@app.post("/api/compress")
async def compress_endpoint(
    file: UploadFile = File(...),
    password: str = Form(...),
    upload_ipfs: bool = Form(True)
):
    """
    Compress and encrypt a file
    
    - **file**: File to compress
    - **password**: Encryption password
    - **upload_ipfs**: Upload to IPFS (default: true)
    """
    temp_dir = None
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        
        # Save uploaded file
        input_path = os.path.join(temp_dir, file.filename)
        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        original_size = len(content)
        
        # Detect file type
        file_info = detect_file_type(input_path)
        
        # Compress
        compressed_data, algorithm, compressed_size = compress_file(input_path, file_info)
        
        # Encrypt
        encryption_result = encrypt_data(compressed_data, password)
        
        # Create metadata
        metadata = {
            "original_filename": file.filename,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_algorithm": algorithm,
            "file_type": file_info['mime_type'],
            "category": file_info['category'],
            "encryption": "AES-256-GCM",
            "salt": encryption_result['salt'],
            "iv": encryption_result['iv'],
            "tag": encryption_result['tag'],
        }
        
        # Create .ppc file
        output_path = os.path.join(temp_dir, f"{file.filename}.ppc")
        create_ppc_file(encryption_result['ciphertext'], metadata, output_path)
        
        # Upload to IPFS if requested
        ipfs_link = None
        if upload_ipfs:
            try:
                ipfs_link = upload_to_ipfs(output_path)
            except Exception as e:
                print(f"IPFS upload failed: {e}")
        
        # Read the .ppc file
        with open(output_path, "rb") as f:
            ppc_content = f.read()
        
        # Save to temp location for download
        download_path = os.path.join(temp_dir, "output.ppc")
        with open(download_path, "wb") as f:
            f.write(ppc_content)
        
        response = FileResponse(
            download_path,
            media_type="application/octet-stream",
            filename=f"{file.filename}.ppc",
            background=None
        )
        
        # Add metadata headers
        response.headers["X-Original-Size"] = str(original_size)
        response.headers["X-Compressed-Size"] = str(compressed_size)
        response.headers["X-Algorithm"] = algorithm
        if ipfs_link:
            response.headers["X-IPFS-Link"] = ipfs_link
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup will happen after response is sent
        pass


@app.post("/api/decompress")
async def decompress_endpoint(
    file: UploadFile = File(...),
    password: str = Form(...)
):
    """
    Decrypt and decompress a .ppc file
    
    - **file**: .ppc file to decompress
    - **password**: Decryption password
    """
    temp_dir = None
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        
        # Save uploaded .ppc file
        ppc_path = os.path.join(temp_dir, file.filename)
        with open(ppc_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Read .ppc file
        with open(ppc_path, "rb") as f:
            ppc_data = f.read()
        
        # Unpack
        unpacked = PPCFile.unpack(ppc_data)
        header = unpacked['header']
        encrypted_data = unpacked['data']
        
        # Decrypt
        decrypted_data = decrypt_data({
            'ciphertext': encrypted_data,
            'salt': header['salt'],
            'iv': header['iv'],
            'tag': header['tag'],
        }, password)
        
        # Decompress
        algorithm = header.get('compression_algorithm', 'none')
        if algorithm != 'none':
            original_data = decompress_file(decrypted_data, algorithm)
        else:
            original_data = decrypted_data
        
        # Save decompressed file
        original_filename = header.get('original_filename', 'restored_file')
        output_path = os.path.join(temp_dir, original_filename)
        with open(output_path, "wb") as f:
            f.write(original_data)
        
        return FileResponse(
            output_path,
            media_type="application/octet-stream",
            filename=original_filename
        )
        
    except Exception as e:
        if "tag" in str(e).lower() or "decrypt" in str(e).lower():
            raise HTTPException(status_code=401, detail="Invalid password or corrupted file")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup will happen after response is sent
        pass


@app.post("/api/info")
async def info_endpoint(file: UploadFile = File(...)):
    """
    Get information about a .ppc file without decrypting
    
    - **file**: .ppc file to analyze
    """
    try:
        content = await file.read()
        unpacked = PPCFile.unpack(content)
        header = unpacked['header']
        
        orig_size = header.get('original_size', 0)
        comp_size = header.get('compressed_size', 0)
        
        ratio = orig_size / comp_size if comp_size > 0 else 1.0
        savings = ((orig_size - comp_size) / orig_size * 100) if orig_size > 0 else 0
        
        return {
            "filename": header.get('original_filename', 'N/A'),
            "file_type": header.get('file_type', 'N/A'),
            "category": header.get('category', 'N/A'),
            "original_size": orig_size,
            "compressed_size": comp_size,
            "compression_ratio": round(ratio, 2),
            "space_saved_percent": round(savings, 1),
            "algorithm": header.get('compression_algorithm', 'N/A'),
            "encryption": header.get('encryption', 'N/A'),
            "version": header.get('version', 'N/A')
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid .ppc file")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
