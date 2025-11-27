"""
CID Verifier
Verify IPFS CIDs and document integrity on blockchain
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib


class CIDVerifier:
    """
    Verify Content Identifiers (CIDs) and document integrity
    """
    
    def __init__(self):
        """Initialize CID verifier"""
        from Blockchain.blockchain.ipfs_handler import IPFSHandler
        from Blockchain.blockchain.smart_contract import SmartContract
        
        self.ipfs_handler = IPFSHandler()
        self.smart_contract = SmartContract()
        self.verification_cache: Dict[str, Dict[str, Any]] = {}
    
    def verify_cid(
        self,
        cid: str,
        land_record_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Verify a CID across IPFS and blockchain
        
        Args:
            cid: IPFS CID to verify
            land_record_id: Associated land record ID (optional)
            
        Returns:
            Verification result
        """
        verification_id = f"{cid}:{land_record_id}" if land_record_id else cid
        
        # Check cache
        if verification_id in self.verification_cache:
            cached = self.verification_cache[verification_id]
            # Return cached result if less than 5 minutes old
            if self._is_recent(cached.get("timestamp")):
                cached["from_cache"] = True
                return cached
        
        # Verify on IPFS
        ipfs_accessible = self.ipfs_handler.verify_cid(cid)
        ipfs_info = self.ipfs_handler.get_document_info(cid)
        
        # Verify on blockchain if land_record_id provided
        blockchain_verified = False
        blockchain_details = {}
        
        if land_record_id:
            blockchain_result = self.smart_contract.verify_land_record(
                land_record_id=land_record_id,
                ipfs_cid=cid
            )
            blockchain_verified = blockchain_result.get("verified", False)
            blockchain_details = blockchain_result
        
        # Create verification result
        result = {
            "verified": ipfs_accessible and (blockchain_verified if land_record_id else True),
            "cid": cid,
            "land_record_id": land_record_id,
            "ipfs_accessible": ipfs_accessible,
            "ipfs_info": ipfs_info,
            "blockchain_verified": blockchain_verified,
            "blockchain_details": blockchain_details,
            "timestamp": datetime.utcnow().isoformat(),
            "from_cache": False
        }
        
        # Cache result
        self.verification_cache[verification_id] = result
        
        return result
    
    def verify_batch(
        self,
        verifications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify multiple CIDs in batch
        
        Args:
            verifications: List of {cid, land_record_id} dictionaries
            
        Returns:
            Batch verification results
        """
        results = []
        verified_count = 0
        failed_count = 0
        
        for item in verifications:
            cid = item.get("cid")
            land_record_id = item.get("land_record_id")
            
            result = self.verify_cid(cid, land_record_id)
            results.append(result)
            
            if result.get("verified"):
                verified_count += 1
            else:
                failed_count += 1
        
        return {
            "total": len(verifications),
            "verified": verified_count,
            "failed": failed_count,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def verify_document_integrity(
        self,
        cid: str,
        expected_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify document integrity using hash
        
        Args:
            cid: IPFS CID
            expected_hash: Expected document hash (optional)
            
        Returns:
            Integrity verification result
        """
        try:
            # Retrieve document from IPFS
            retrieval = self.ipfs_handler.retrieve_document(cid)
            
            if not retrieval.get("success"):
                return {
                    "verified": False,
                    "error": "Failed to retrieve document from IPFS"
                }
            
            document_data = retrieval.get("data")
            
            # Calculate document hash
            document_hash = hashlib.sha256(document_data).hexdigest()
            
            # Verify against expected hash if provided
            hash_matches = True
            if expected_hash:
                hash_matches = document_hash == expected_hash
            
            return {
                "verified": hash_matches,
                "cid": cid,
                "document_hash": document_hash,
                "expected_hash": expected_hash,
                "hash_matches": hash_matches,
                "document_size": len(document_data),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "verified": False,
                "error": str(e)
            }
    
    def create_verification_certificate(
        self,
        cid: str,
        land_record_id: int
    ) -> Dict[str, Any]:
        """
        Create a verification certificate for audit purposes
        
        Args:
            cid: IPFS CID
            land_record_id: Land record ID
            
        Returns:
            Verification certificate
        """
        # Perform comprehensive verification
        verification = self.verify_cid(cid, land_record_id)
        
        # Get audit trail
        audit_proof = self.smart_contract.create_audit_proof(land_record_id)
        
        # Create certificate hash
        certificate_data = f"{cid}:{land_record_id}:{datetime.utcnow().isoformat()}"
        certificate_hash = hashlib.sha256(certificate_data.encode()).hexdigest()
        
        return {
            "certificate_id": certificate_hash,
            "cid": cid,
            "land_record_id": land_record_id,
            "verification_result": verification,
            "audit_proof": audit_proof,
            "issued_at": datetime.utcnow().isoformat(),
            "valid": verification.get("verified", False),
            "certificate_hash": certificate_hash
        }
    
    def _is_recent(self, timestamp: str, minutes: int = 5) -> bool:
        """Check if timestamp is within specified minutes"""
        try:
            ts = datetime.fromisoformat(timestamp)
            now = datetime.utcnow()
            diff = (now - ts).total_seconds() / 60
            return diff < minutes
        except:
            return False
    
    def clear_cache(self):
        """Clear verification cache"""
        self.verification_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cached_verifications": len(self.verification_cache),
            "cache_keys": list(self.verification_cache.keys())
        }


# Convenience functions
def quick_verify_cid(
    cid: str,
    land_record_id: Optional[int] = None
) -> bool:
    """
    Quick CID verification
    
    Args:
        cid: IPFS CID
        land_record_id: Land record ID (optional)
        
    Returns:
        True if verified
    """
    verifier = CIDVerifier()
    result = verifier.verify_cid(cid, land_record_id)
    return result.get("verified", False)


def verify_and_certify(
    cid: str,
    land_record_id: int
) -> Dict[str, Any]:
    """
    Verify and generate certificate
    
    Args:
        cid: IPFS CID
        land_record_id: Land record ID
        
    Returns:
        Verification certificate
    """
    verifier = CIDVerifier()
    return verifier.create_verification_certificate(cid, land_record_id)