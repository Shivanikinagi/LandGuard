"""
Compression Bridge
Integrates LandGuard with PCC compression system
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import json

# Add PCC to path
pcc_path = Path(__file__).parent.parent.parent.parent / "pcc"
if str(pcc_path) not in sys.path:
    sys.path.insert(0, str(pcc_path))

try:
    from crypto.aes import encrypt_data, decrypt_data
    from core.ppc_format import create_ppc_file, read_ppc_file
    from detector.file_type import detect_file_type
    from compressors.compressor import compress_file
    from storage.ipfs_client import upload_to_ipfs
except ImportError as e:
    print(f"Warning: PCC modules not available: {e}")


class CompressionBridge:
    """
    Bridge between LandGuard and PCC compression system
    Handles compression, encryption, and .ppc file creation for land documents
    """
    
    def __init__(self, password: str = "landguard_default"):
        """
        Initialize compression bridge
        
        Args:
            password: Encryption password for .ppc files
        """
        self.password = password
        self.pcc_available = self._check_pcc_availability()
    
    def _check_pcc_availability(self) -> bool:
        """Check if PCC modules are available"""
        try:
            from crypto.aes import encrypt_data
            return True
        except ImportError:
            return False
    
    def compress_and_encrypt(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Compress and encrypt a land document
        
        Args:
            input_path: Path to input file
            output_path: Path for output .ppc file (optional)
            metadata: Additional metadata to include
            
        Returns:
            Tuple of (success, output_path, compression_info)
        """
        if not self.pcc_available:
            return False, "", {"error": "PCC not available"}
        
        try:
            # Read input file
            with open(input_path, 'rb') as f:
                data = f.read()
            
            # Detect file type
            file_info = detect_file_type(input_path)
            
            # Compress data using actual PCC compression
            compressed_data, model_used, compressed_size = compress_file(input_path, file_info)
            compression_ratio = len(data) / compressed_size if compressed_size > 0 else 1.0
            
            # Encrypt data
            encrypted_data = encrypt_data(compressed_data, self.password)
            
            # Prepare metadata
            ppc_metadata = {
                "original_filename": Path(input_path).name,
                "original_mime_type": file_info.get("mime_type", "application/octet-stream"),
                "file_type": file_info.get("category", "unknown"),
                "original_size_bytes": len(data),
                "compressed_size_bytes": compressed_size,
                "compression_ratio": compression_ratio,
                "encryption_algo": "AES-256-GCM",
                "model_used": model_used
            }
            
            # Add custom metadata
            if metadata:
                ppc_metadata.update(metadata)
            
            # Create output path
            if not output_path:
                output_path = f"{input_path}.ppc"
            
            # Create .ppc file
            create_ppc_file(encrypted_data, ppc_metadata, output_path)
            
            return True, output_path, ppc_metadata
            
        except Exception as e:
            return False, "", {"error": str(e)}
    
    def decrypt_and_decompress(
        self,
        ppc_path: str,
        output_path: Optional[str] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Decrypt and decompress a .ppc file
        
        Args:
            ppc_path: Path to .ppc file
            output_path: Path for output file (optional)
            
        Returns:
            Tuple of (success, output_path, metadata)
        """
        if not self.pcc_available:
            return False, "", {"error": "PCC not available"}
        
        try:
            # Read .ppc file
            encrypted_data, metadata = read_ppc_file(ppc_path)
            
            # Decrypt data
            compressed_data = decrypt_data(encrypted_data, self.password)
            
            # Decompress data
            from compressors.decompressor import decompress_data
            original_data = decompress_data(compressed_data, metadata)
            
            # Create output path
            if not output_path:
                original_filename = metadata.get("original_filename", "output")
                output_path = str(Path(ppc_path).parent / original_filename)
            
            # Write output file
            with open(output_path, 'wb') as f:
                f.write(original_data)
            
            return True, output_path, metadata
            
        except Exception as e:
            return False, "", {"error": str(e)}
    
    def process_and_upload_to_ipfs(
        self,
        input_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Process document through complete PCC workflow and upload to IPFS
        
        Args:
            input_path: Path to input file
            metadata: Additional metadata to include
            
        Returns:
            Tuple of (success, ipfs_url, result_info)
        """
        if not self.pcc_available:
            return False, "", {"error": "PCC not available"}
        
        try:
            # Step 1: Compress and encrypt
            success, ppc_path, compression_info = self.compress_and_encrypt(
                input_path, 
                metadata=metadata
            )
            
            if not success:
                return False, "", {"error": "Compression failed", "details": compression_info}
            
            # Step 2: Upload to IPFS
            ipfs_url = upload_to_ipfs(ppc_path)
            
            # Extract CID from URL
            cid = ipfs_url.split("/")[-1] if ipfs_url else None
            
            result_info = {
                "ppc_path": ppc_path,
                "ipfs_url": ipfs_url,
                "cid": cid,
                "compression_info": compression_info
            }
            
            return True, ipfs_url, result_info
            
        except Exception as e:
            return False, "", {"error": str(e)}
    
    def get_ppc_metadata(self, ppc_path: str) -> Dict[str, Any]:
        """
        Get metadata from .ppc file without decrypting
        
        Args:
            ppc_path: Path to .ppc file
            
        Returns:
            Metadata dictionary
        """
        try:
            _, metadata = read_ppc_file(ppc_path)
            return metadata
        except Exception as e:
            return {"error": str(e)}


def compress_land_document(
    input_path: str,
    password: str = "landguard_default",
    land_record_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Convenience function to compress a land document
    
    Args:
        input_path: Path to document
        password: Encryption password
        land_record_id: Associated land record ID
        
    Returns:
        Result dictionary with status and info
    """
    bridge = CompressionBridge(password)
    
    metadata = {}
    if land_record_id:
        metadata["land_record_id"] = land_record_id
    
    success, output_path, info = bridge.compress_and_encrypt(
        input_path,
        metadata=metadata
    )
    
    return {
        "success": success,
        "output_path": output_path,
        "metadata": info
    }


def decompress_land_document(
    ppc_path: str,
    password: str = "landguard_default"
) -> Dict[str, Any]:
    """
    Convenience function to decompress a land document
    
    Args:
        ppc_path: Path to .ppc file
        password: Decryption password
        
    Returns:
        Result dictionary with status and info
    """
    bridge = CompressionBridge(password)
    
    success, output_path, metadata = bridge.decrypt_and_decompress(ppc_path)
    
    return {
        "success": success,
        "output_path": output_path,
        "metadata": metadata
    }


def process_document_complete_workflow(
    input_path: str,
    password: str = "landguard_default",
    land_record_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Process document through complete workflow: compress -> encrypt -> create .ppc -> upload to IPFS
    
    Args:
        input_path: Path to document
        password: Encryption password
        land_record_id: Associated land record ID
        
    Returns:
        Result dictionary with status and info
    """
    bridge = CompressionBridge(password)
    
    metadata = {}
    if land_record_id:
        metadata["land_record_id"] = land_record_id
    
    success, ipfs_url, info = bridge.process_and_upload_to_ipfs(
        input_path,
        metadata=metadata
    )
    
    return {
        "success": success,
        "ipfs_url": ipfs_url,
        "details": info
    }