"""
IPFS Handler
Manages IPFS uploads and retrievals for land documents
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import requests
import os
from datetime import datetime

# Add PCC to path for IPFS client
pcc_path = Path(__file__).parent.parent.parent.parent / "pcc"
if str(pcc_path) not in sys.path:
    sys.path.insert(0, str(pcc_path))

try:
    from storage.ipfs_client import upload_to_ipfs, get_from_ipfs
except ImportError:
    upload_to_ipfs = None
    get_from_ipfs = None


class IPFSHandler:
    """
    Handle IPFS operations for blockchain integration
    """
    
    def __init__(self):
        """Initialize IPFS handler"""
        self.gateway_url = "https://gateway.pinata.cloud/ipfs"
        self.ipfs_available = upload_to_ipfs is not None
    
    def upload_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload a document to IPFS
        
        Args:
            file_path: Path to file to upload
            metadata: Additional metadata
            
        Returns:
            Result dictionary with CID and status
        """
        if not self.ipfs_available:
            return {
                "success": False,
                "error": "IPFS client not available",
                "cid": None
            }
        
        try:
            # Upload file to IPFS
            cid = upload_to_ipfs(file_path)
            
            if not cid:
                return {
                    "success": False,
                    "error": "Failed to upload to IPFS",
                    "cid": None
                }
            
            # Prepare result
            result = {
                "success": True,
                "cid": cid,
                "ipfs_url": f"{self.gateway_url}/{cid}",
                "timestamp": datetime.utcnow().isoformat(),
                "file_name": Path(file_path).name,
                "file_size": Path(file_path).stat().st_size
            }
            
            # Add metadata
            if metadata:
                result["metadata"] = metadata
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "cid": None
            }
    
    def retrieve_document(
        self,
        cid: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve a document from IPFS
        
        Args:
            cid: IPFS CID
            output_path: Path to save retrieved file
            
        Returns:
            Result dictionary with status
        """
        if not self.ipfs_available:
            return {
                "success": False,
                "error": "IPFS client not available"
            }
        
        try:
            # Download from IPFS
            url = f"{self.gateway_url}/{cid}"
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to retrieve from IPFS: {response.status_code}"
                }
            
            # Save to file
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                return {
                    "success": True,
                    "output_path": output_path,
                    "size": len(response.content)
                }
            else:
                return {
                    "success": True,
                    "data": response.content,
                    "size": len(response.content)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_cid(self, cid: str) -> bool:
        """
        Verify if a CID is accessible on IPFS
        
        Args:
            cid: IPFS CID to verify
            
        Returns:
            True if accessible, False otherwise
        """
        try:
            url = f"{self.gateway_url}/{cid}"
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_document_info(self, cid: str) -> Dict[str, Any]:
        """
        Get information about a document on IPFS
        
        Args:
            cid: IPFS CID
            
        Returns:
            Information dictionary
        """
        try:
            url = f"{self.gateway_url}/{cid}"
            response = requests.head(url, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "cid": cid,
                    "url": url,
                    "accessible": True,
                    "size": response.headers.get('Content-Length'),
                    "content_type": response.headers.get('Content-Type')
                }
            else:
                return {
                    "success": False,
                    "cid": cid,
                    "accessible": False,
                    "error": f"Status code: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "cid": cid,
                "accessible": False,
                "error": str(e)
            }


# Convenience functions
def upload_land_document_to_ipfs(
    file_path: str,
    land_record_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Upload a land document to IPFS
    
    Args:
        file_path: Path to document
        land_record_id: Associated land record ID
        
    Returns:
        Upload result
    """
    handler = IPFSHandler()
    
    metadata = {}
    if land_record_id:
        metadata["land_record_id"] = land_record_id
        metadata["document_type"] = "land_record"
    
    return handler.upload_document(file_path, metadata)


def retrieve_land_document_from_ipfs(
    cid: str,
    output_path: str
) -> Dict[str, Any]:
    """
    Retrieve a land document from IPFS
    
    Args:
        cid: IPFS CID
        output_path: Path to save document
        
    Returns:
        Retrieval result
    """
    handler = IPFSHandler()
    return handler.retrieve_document(cid, output_path)


def verify_land_document_cid(cid: str) -> bool:
    """
    Verify if a land document CID is accessible
    
    Args:
        cid: IPFS CID
        
    Returns:
        True if accessible
    """
    handler = IPFSHandler()
    return handler.verify_cid(cid)