"""
Compression Agent
Autonomous agent for compressing and encrypting land documents
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any
from .base_agent import BaseAgent

# Add PCC to path for compression functionality
pcc_path = Path(__file__).parent.parent.parent / "pcc"
if str(pcc_path) not in sys.path:
    sys.path.insert(0, str(pcc_path))

class CompressionAgent(BaseAgent):
    """Agent responsible for compressing and encrypting documents"""
    
    def __init__(self, password: str = "landguard_default"):
        super().__init__(
            name="compression_agent",
            capabilities=["compression", "encryption", "file_processing"]
        )
        self.password = password
        self.pcc_available = self._check_pcc_availability()
        
    def _check_pcc_availability(self) -> bool:
        """Check if PCC modules are available"""
        try:
            from crypto.aes import encrypt_data
            from core.ppc_format import create_ppc_file
            return True
        except ImportError:
            return False
            
    async def process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compress and encrypt a document
        
        Args:
            task_data: Contains file path and metadata
            
        Returns:
            Dictionary with compression results
        """
        file_path = task_data.get("file_path")
        encrypt = task_data.get("encrypt", True)
        compress = task_data.get("compress", True)
        
        if not file_path or not os.path.exists(file_path):
            return {
                "success": False,
                "error": "File not found",
                "file_path": file_path
            }
            
        self.logger.info(f"Processing compression for {file_path}")
        
        if self.pcc_available and encrypt:
            result = self._process_with_pcc(file_path, task_data.get("metadata", {}))
        else:
            result = self._process_simple(file_path, task_data.get("metadata", {}))
            
        self.log_task(task_data, result)
        return result
        
    def _process_with_pcc(self, file_path: str, metadata: Dict) -> Dict[str, Any]:
        """Process file using PCC compression system"""
        try:
            from core.ppc_format import create_ppc_file
            from crypto.aes import encrypt_data
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            original_size = len(file_content)
            
            # Encrypt the file content
            self.logger.info("Encrypting file content...")
            encrypted_dict = encrypt_data(file_content, self.password)
            
            # Get the ciphertext
            ciphertext = encrypted_dict["ciphertext"]
            
            # Create metadata for PPC file
            ppc_metadata = {
                "original_filename": os.path.basename(file_path),
                "original_size": original_size,
                "encrypted_size": len(ciphertext),
                "encryption": "AES-256-GCM",
                "salt": encrypted_dict["salt"].hex(),
                "iv": encrypted_dict["iv"].hex(),
                "tag": encrypted_dict["tag"].hex(),
                "processed_by": "compression_agent",
                **metadata
            }
            
            # Create output path
            output_path = f"{file_path}.ppc"
            
            # Create PPC file with encrypted data
            self.logger.info(f"Creating PPC file: {output_path}")
            create_ppc_file(ciphertext, ppc_metadata, output_path)
            
            compression_ratio = round(original_size / len(ciphertext), 2) if len(ciphertext) > 0 else 1.0
            space_saved = round((1 - len(ciphertext) / original_size) * 100, 1) if original_size > 0 else 0
            
            return {
                "success": True,
                "output_path": output_path,
                "original_size": original_size,
                "compressed_size": len(ciphertext),
                "compression_ratio": compression_ratio,
                "space_saved_percent": space_saved,
                "method": "PCC_AES256_GCM"
            }
            
        except Exception as e:
            self.logger.error(f"PCC processing failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "method": "PCC_AES256_GCM"
            }
            
    def _process_simple(self, file_path: str, metadata: Dict) -> Dict[str, Any]:
        """Fallback processing without PCC"""
        try:
            # Read file
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            original_size = len(file_content)
            
            # Simple XOR encryption for fallback
            encrypted_content = bytearray(file_content)
            for i in range(len(encrypted_content)):
                encrypted_content[i] ^= ord(self.password[i % len(self.password)])
            
            # Save encrypted file
            output_path = f"{file_path}.enc"
            with open(output_path, 'wb') as f:
                f.write(encrypted_content)
            
            return {
                "success": True,
                "output_path": output_path,
                "original_size": original_size,
                "compressed_size": len(encrypted_content),
                "compression_ratio": 1.0,
                "space_saved_percent": 0.0,
                "method": "SIMPLE_XOR"
            }
            
        except Exception as e:
            self.logger.error(f"Simple processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "method": "SIMPLE_XOR"
            }