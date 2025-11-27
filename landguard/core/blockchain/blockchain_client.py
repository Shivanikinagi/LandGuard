"""
Blockchain Client
High-level client for blockchain operations in LandGuard
"""

from typing import Optional, Dict, Any
from datetime import datetime


class BlockchainClient:
    """
    Unified client for blockchain operations
    Integrates smart contracts, transactions, and IPFS
    """
    
    def __init__(self, sandbox_mode: bool = True):
        """
        Initialize blockchain client
        
        Args:
            sandbox_mode: Use sandbox/mock blockchain (default: True)
        """
        self.sandbox_mode = sandbox_mode
        
        # Import blockchain components
        from Blockchain.blockchain.smart_contract import SmartContract
        from Blockchain.blockchain.transaction_handler import TransactionHandler
        from Blockchain.blockchain.ipfs_handler import IPFSHandler
        
        self.smart_contract = SmartContract()
        self.transaction_handler = TransactionHandler()
        self.ipfs_handler = IPFSHandler()
    
    def register_complete_record(
        self,
        land_record_id: int,
        file_path: str,
        owner_address: str = "0x000",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete workflow: Upload to IPFS and register on blockchain
        
        Args:
            land_record_id: Land record ID
            file_path: Path to document file
            owner_address: Owner's blockchain address
            metadata: Additional metadata
            
        Returns:
            Complete registration result
        """
        try:
            # Step 1: Upload to IPFS
            ipfs_result = self.ipfs_handler.upload_document(
                file_path=file_path,
                metadata=metadata
            )
            
            if not ipfs_result.get("success"):
                return {
                    "success": False,
                    "stage": "ipfs_upload",
                    "error": ipfs_result.get("error")
                }
            
            ipfs_cid = ipfs_result.get("cid")
            
            # Step 2: Register on blockchain
            blockchain_result = self.smart_contract.register_land_record(
                land_record_id=land_record_id,
                ipfs_cid=ipfs_cid,
                owner_address=owner_address,
                metadata=metadata
            )
            
            if not blockchain_result.get("success"):
                return {
                    "success": False,
                    "stage": "blockchain_registration",
                    "ipfs_cid": ipfs_cid,
                    "error": blockchain_result.get("error")
                }
            
            # Step 3: Create transaction record
            tx_result = self.transaction_handler.create_and_submit(
                transaction_type="register",
                land_record_id=land_record_id,
                data={
                    "ipfs_cid": ipfs_cid,
                    "owner_address": owner_address
                }
            )
            
            return {
                "success": True,
                "land_record_id": land_record_id,
                "ipfs_cid": ipfs_cid,
                "ipfs_url": ipfs_result.get("ipfs_url"),
                "tx_hash": blockchain_result.get("tx_hash"),
                "block_number": blockchain_result.get("block_number"),
                "transaction_id": tx_result.get("tx_id"),
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Land record successfully registered on blockchain"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_complete_record(
        self,
        land_record_id: int,
        ipfs_cid: str
    ) -> Dict[str, Any]:
        """
        Verify land record across IPFS and blockchain
        
        Args:
            land_record_id: Land record ID
            ipfs_cid: IPFS CID to verify
            
        Returns:
            Verification result
        """
        # Verify on IPFS
        ipfs_accessible = self.ipfs_handler.verify_cid(ipfs_cid)
        
        # Verify on blockchain
        blockchain_result = self.smart_contract.verify_land_record(
            land_record_id=land_record_id,
            ipfs_cid=ipfs_cid
        )
        
        both_verified = ipfs_accessible and blockchain_result.get("verified", False)
        
        return {
            "verified": both_verified,
            "land_record_id": land_record_id,
            "ipfs_cid": ipfs_cid,
            "ipfs_accessible": ipfs_accessible,
            "blockchain_verified": blockchain_result.get("verified", False),
            "blockchain_details": blockchain_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_record_audit_trail(
        self,
        land_record_id: int
    ) -> Dict[str, Any]:
        """
        Get complete audit trail for a land record
        
        Args:
            land_record_id: Land record ID
            
        Returns:
            Complete audit trail
        """
        # Get blockchain history
        blockchain_history = self.smart_contract.get_record_history(land_record_id)
        
        # Get transaction history
        transaction_history = self.transaction_handler.get_transaction_history(
            land_record_id=land_record_id
        )
        
        # Create audit proof
        audit_proof = self.smart_contract.create_audit_proof(land_record_id)
        
        return {
            "land_record_id": land_record_id,
            "blockchain_history": blockchain_history,
            "transaction_history": transaction_history,
            "audit_proof": audit_proof,
            "total_transactions": len(blockchain_history) + len(transaction_history),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def update_record(
        self,
        land_record_id: int,
        new_file_path: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update a land record with new document
        
        Args:
            land_record_id: Land record ID
            new_file_path: Path to new document
            reason: Reason for update
            metadata: Additional metadata
            
        Returns:
            Update result
        """
        try:
            # Upload new version to IPFS
            ipfs_result = self.ipfs_handler.upload_document(
                file_path=new_file_path,
                metadata=metadata
            )
            
            if not ipfs_result.get("success"):
                return {
                    "success": False,
                    "error": ipfs_result.get("error")
                }
            
            new_cid = ipfs_result.get("cid")
            
            # Update on blockchain
            blockchain_result = self.smart_contract.update_land_record(
                land_record_id=land_record_id,
                new_ipfs_cid=new_cid,
                reason=reason
            )
            
            # Create transaction
            tx_result = self.transaction_handler.create_and_submit(
                transaction_type="update",
                land_record_id=land_record_id,
                data={
                    "new_ipfs_cid": new_cid,
                    "reason": reason
                }
            )
            
            return {
                "success": True,
                "land_record_id": land_record_id,
                "new_ipfs_cid": new_cid,
                "old_ipfs_cid": blockchain_result.get("old_cid"),
                "tx_hash": blockchain_result.get("tx_hash"),
                "transaction_id": tx_result.get("tx_id"),
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get blockchain client statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            "pending_transactions": self.transaction_handler.get_pending_count(),
            "completed_transactions": self.transaction_handler.get_completed_count(),
            "failed_transactions": self.transaction_handler.get_failed_count(),
            "total_records": len(self.smart_contract._sandbox_records),
            "sandbox_mode": self.sandbox_mode,
            "timestamp": datetime.utcnow().isoformat()
        }


# Convenience functions
def quick_register(
    land_record_id: int,
    file_path: str
) -> Dict[str, Any]:
    """
    Quick registration of land document
    
    Args:
        land_record_id: Land record ID
        file_path: Path to document
        
    Returns:
        Registration result
    """
    client = BlockchainClient()
    return client.register_complete_record(
        land_record_id=land_record_id,
        file_path=file_path
    )


def quick_verify(
    land_record_id: int,
    ipfs_cid: str
) -> bool:
    """
    Quick verification of land document
    
    Args:
        land_record_id: Land record ID
        ipfs_cid: IPFS CID
        
    Returns:
        True if verified
    """
    client = BlockchainClient()
    result = client.verify_complete_record(land_record_id, ipfs_cid)
    return result.get("verified", False)