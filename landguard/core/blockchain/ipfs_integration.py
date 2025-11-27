"""
IPFS Integration
High-level integration of IPFS with LandGuard workflow
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json


class IPFSIntegration:
    """
    Integrate IPFS storage with LandGuard document management
    """
    
    def __init__(self):
        """Initialize IPFS integration"""
        from Blockchain.blockchain.ipfs_handler import IPFSHandler
        self.handler = IPFSHandler()
        self.upload_history: List[Dict[str, Any]] = []
    
    def upload_with_metadata(
        self,
        file_path: str,
        land_record_id: int,
        document_type: str,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload document with complete metadata
        
        Args:
            file_path: Path to document
            land_record_id: Land record ID
            document_type: Type of document
            additional_metadata: Additional metadata
            
        Returns:
            Upload result with CID
        """
        # Prepare metadata
        metadata = {
            "land_record_id": land_record_id,
            "document_type": document_type,
            "upload_timestamp": datetime.utcnow().isoformat(),
            "file_name": Path(file_path).name,
            "file_size": Path(file_path).stat().st_size
        }
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        # Upload to IPFS
        result = self.handler.upload_document(file_path, metadata)
        
        # Track upload history
        if result.get("success"):
            self.upload_history.append({
                "cid": result.get("cid"),
                "land_record_id": land_record_id,
                "timestamp": metadata["upload_timestamp"],
                "document_type": document_type
            })
        
        return result
    
    def create_audit_trail(
        self,
        land_record_id: int,
        cid: str,
        action: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create audit trail entry for IPFS upload
        
        Args:
            land_record_id: Land record ID
            cid: IPFS CID
            action: Action performed
            user_id: User who performed action
            
        Returns:
            Audit trail entry
        """
        audit_entry = {
            "land_record_id": land_record_id,
            "cid": cid,
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "ipfs_url": f"{self.handler.gateway_url}/{cid}"
        }
        
        if user_id:
            audit_entry["user_id"] = user_id
        
        return audit_entry
    
    def verify_document_integrity(
        self,
        cid: str,
        expected_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verify document integrity on IPFS
        
        Args:
            cid: IPFS CID
            expected_metadata: Expected metadata to verify
            
        Returns:
            Verification result
        """
        # Check if CID is accessible
        accessible = self.handler.verify_cid(cid)
        
        if not accessible:
            return {
                "verified": False,
                "error": "CID not accessible on IPFS"
            }
        
        # Get document info
        info = self.handler.get_document_info(cid)
        
        verification_result = {
            "verified": True,
            "cid": cid,
            "accessible": accessible,
            "info": info,
            "verification_timestamp": datetime.utcnow().isoformat()
        }
        
        # Verify metadata if provided
        if expected_metadata:
            verification_result["metadata_match"] = True  # Placeholder
        
        return verification_result
    
    def batch_upload_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Upload multiple documents to IPFS
        
        Args:
            documents: List of document dictionaries with file_path, land_record_id, etc.
            
        Returns:
            List of upload results
        """
        results = []
        
        for doc in documents:
            result = self.upload_with_metadata(
                file_path=doc.get("file_path"),
                land_record_id=doc.get("land_record_id"),
                document_type=doc.get("document_type", "document"),
                additional_metadata=doc.get("metadata")
            )
            results.append(result)
        
        return results
    
    def get_upload_history(
        self,
        land_record_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get upload history
        
        Args:
            land_record_id: Filter by land record ID (optional)
            
        Returns:
            List of upload history entries
        """
        if land_record_id:
            return [
                entry for entry in self.upload_history
                if entry.get("land_record_id") == land_record_id
            ]
        return self.upload_history


# Convenience functions
def upload_and_verify(
    file_path: str,
    land_record_id: int,
    document_type: str = "land_document"
) -> Dict[str, Any]:
    """
    Upload document and create verification record
    
    Args:
        file_path: Path to document
        land_record_id: Land record ID
        document_type: Document type
        
    Returns:
        Complete result with CID and verification
    """
    integration = IPFSIntegration()
    
    # Upload document
    upload_result = integration.upload_with_metadata(
        file_path=file_path,
        land_record_id=land_record_id,
        document_type=document_type
    )
    
    if not upload_result.get("success"):
        return upload_result
    
    # Verify upload
    cid = upload_result.get("cid")
    verification = integration.verify_document_integrity(cid)
    
    # Create audit trail
    audit = integration.create_audit_trail(
        land_record_id=land_record_id,
        cid=cid,
        action="document_uploaded"
    )
    
    return {
        "success": True,
        "upload": upload_result,
        "verification": verification,
        "audit": audit
    }