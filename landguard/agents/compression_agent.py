"""
Compression Agent
Autonomous agent for compressing and encrypting land documents
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Tuple
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
        if not file_path or not os.path.exists(file_path):
            return {
                "success": False,
                "error": "File not found",
                "file_path": file_path
            }
            
        self.logger.info(f"Processing compression for {file_path}")
        
        if self.pcc_available:
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
            import json
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
                
            # Create PPC file with metadata
            ppc_data = create_ppc_file(
                original_data=file_content,
                metadata={
                    **metadata,
                    "original_filename": os.path.basename(file_path),
                    "processed_by": "compression_agent",
                    "agent_version": "1.0"
                }
            )
            
            # Encrypt the PPC data
            encrypted_dict = encrypt_data(ppc_data, self.password)
            
            # Combine encryption metadata with ciphertext as bytes
            encrypted_package = {
                "ciphertext": encrypted_dict["ciphertext"],
                "salt": encrypted_dict["salt"],
                "iv": encrypted_dict["iv"],
                "tag": encrypted_dict["tag"]
            }
            
            # Save encrypted file as JSON for proper deserialization
            output_path = f"{file_path}.ppc"
            with open(output_path, 'wb') as f:
                # Store as JSON with base64-encoded binary data
                json_data = {
                    "ciphertext": encrypted_dict["ciphertext"].hex(),
                    "salt": encrypted_dict["salt"],
                    "iv": encrypted_dict["iv"],
                    "tag": encrypted_dict["tag"]
                }
                f.write(json.dumps(json_data).encode('utf-8'))
                
            return {
                "success": True,
                "output_path": output_path,
                "original_size": len(file_content),
                "compressed_size": len(encrypted_dict["ciphertext"]),
                "compression_ratio": round(len(encrypted_dict["ciphertext"]) / len(file_content), 2) if len(file_content) > 0 else 1.0,
                "method": "PCC_AES256"
            }
            
        except Exception as e:
            self.logger.error(f"PCC processing failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "method": "PCC_AES256"
            }
            
    def _process_simple(self, file_path: str, metadata: Dict) -> Dict[str, Any]:
        """Fallback processing without PCC"""
        try:
            # Simple encryption simulation
            with open(file_path, 'rb') as f:
                file_content = f.read()
                
            # Simple "encryption" (just for demo)
            encrypted_content = bytearray(file_content)
            for i in range(len(encrypted_content)):
                encrypted_content[i] ^= ord(self.password[i % len(self.password)])
                
            # Save encrypted file
            output_path = f"{file_path}.ppc"
            with open(output_path, 'wb') as f:
                f.write(encrypted_content)
                
            return {
                "success": True,
                "output_path": output_path,
                "original_size": len(file_content),
                "compressed_size": len(encrypted_content),
                "compression_ratio": 1.0,  # No compression in fallback
                "method": "SIMPLE_XOR"
            }
            
        except Exception as e:
            self.logger.error(f"Simple processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "method": "SIMPLE_XOR"
            }