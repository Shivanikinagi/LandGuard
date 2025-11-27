"""
Smart Contract Interface
Interface for interacting with blockchain smart contracts for land record verification
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib
import json


class SmartContract:
    """
    Interface for blockchain smart contract operations
    Currently implements a mock/sandbox version for development
    """
    
    def __init__(self, contract_address: Optional[str] = None):
        """
        Initialize smart contract interface
        
        Args:
            contract_address: Smart contract address (sandbox mode if None)
        """
        self.contract_address = contract_address or "0x0000000000000000000000000000000000000000"
        self.sandbox_mode = contract_address is None
        self.transaction_history: List[Dict[str, Any]] = []
        
        # Sandbox storage
        self._sandbox_records: Dict[str, Dict[str, Any]] = {}
    
    def register_land_record(
        self,
        land_record_id: int,
        ipfs_cid: str,
        owner_address: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register a land record on blockchain
        
        Args:
            land_record_id: Unique land record ID
            ipfs_cid: IPFS CID of the document
            owner_address: Blockchain address of owner
            metadata: Additional metadata
            
        Returns:
            Transaction result
        """
        # Create transaction hash
        tx_data = f"{land_record_id}:{ipfs_cid}:{owner_address}:{datetime.utcnow().isoformat()}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        # Prepare record
        record = {
            "land_record_id": land_record_id,
            "ipfs_cid": ipfs_cid,
            "owner_address": owner_address,
            "timestamp": datetime.utcnow().isoformat(),
            "tx_hash": tx_hash,
            "block_number": len(self.transaction_history) + 1,
            "status": "confirmed"
        }
        
        if metadata:
            record["metadata"] = metadata
        
        # Store in sandbox
        if self.sandbox_mode:
            record_key = f"land_{land_record_id}"
            self._sandbox_records[record_key] = record
        
        # Add to transaction history
        self.transaction_history.append(record)
        
        return {
            "success": True,
            "tx_hash": tx_hash,
            "block_number": record["block_number"],
            "land_record_id": land_record_id,
            "ipfs_cid": ipfs_cid,
            "message": "Land record registered on blockchain"
        }
    
    def verify_land_record(
        self,
        land_record_id: int,
        ipfs_cid: str
    ) -> Dict[str, Any]:
        """
        Verify a land record on blockchain
        
        Args:
            land_record_id: Land record ID to verify
            ipfs_cid: IPFS CID to verify
            
        Returns:
            Verification result
        """
        if self.sandbox_mode:
            record_key = f"land_{land_record_id}"
            record = self._sandbox_records.get(record_key)
            
            if not record:
                return {
                    "verified": False,
                    "error": "Land record not found on blockchain"
                }
            
            cid_matches = record.get("ipfs_cid") == ipfs_cid
            
            return {
                "verified": cid_matches,
                "land_record_id": land_record_id,
                "stored_cid": record.get("ipfs_cid"),
                "provided_cid": ipfs_cid,
                "match": cid_matches,
                "timestamp": record.get("timestamp"),
                "tx_hash": record.get("tx_hash"),
                "block_number": record.get("block_number")
            }
        
        # For non-sandbox mode, would connect to actual blockchain
        return {
            "verified": False,
            "error": "Blockchain connection not implemented"
        }
    
    def update_land_record(
        self,
        land_record_id: int,
        new_ipfs_cid: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Update a land record on blockchain
        
        Args:
            land_record_id: Land record ID
            new_ipfs_cid: New IPFS CID
            reason: Reason for update
            
        Returns:
            Update result
        """
        # Create transaction hash
        tx_data = f"UPDATE:{land_record_id}:{new_ipfs_cid}:{reason}:{datetime.utcnow().isoformat()}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        update_record = {
            "action": "update",
            "land_record_id": land_record_id,
            "new_ipfs_cid": new_ipfs_cid,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "tx_hash": tx_hash,
            "block_number": len(self.transaction_history) + 1
        }
        
        # Update in sandbox
        if self.sandbox_mode:
            record_key = f"land_{land_record_id}"
            if record_key in self._sandbox_records:
                old_cid = self._sandbox_records[record_key].get("ipfs_cid")
                self._sandbox_records[record_key]["ipfs_cid"] = new_ipfs_cid
                self._sandbox_records[record_key]["previous_cid"] = old_cid
                self._sandbox_records[record_key]["updated_at"] = update_record["timestamp"]
                update_record["old_cid"] = old_cid
        
        self.transaction_history.append(update_record)
        
        return {
            "success": True,
            "tx_hash": tx_hash,
            "block_number": update_record["block_number"],
            "message": "Land record updated on blockchain"
        }
    
    def get_record_history(
        self,
        land_record_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get complete history of a land record
        
        Args:
            land_record_id: Land record ID
            
        Returns:
            List of all transactions for this record
        """
        history = [
            tx for tx in self.transaction_history
            if tx.get("land_record_id") == land_record_id
        ]
        return history
    
    def get_transaction_by_hash(
        self,
        tx_hash: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get transaction details by hash
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction details or None
        """
        for tx in self.transaction_history:
            if tx.get("tx_hash") == tx_hash:
                return tx
        return None
    
    def create_audit_proof(
        self,
        land_record_id: int
    ) -> Dict[str, Any]:
        """
        Create cryptographic audit proof for a land record
        
        Args:
            land_record_id: Land record ID
            
        Returns:
            Audit proof
        """
        history = self.get_record_history(land_record_id)
        
        if not history:
            return {
                "success": False,
                "error": "No history found for land record"
            }
        
        # Create proof hash
        proof_data = json.dumps(history, sort_keys=True)
        proof_hash = hashlib.sha256(proof_data.encode()).hexdigest()
        
        return {
            "success": True,
            "land_record_id": land_record_id,
            "proof_hash": proof_hash,
            "transaction_count": len(history),
            "first_registration": history[0].get("timestamp"),
            "latest_update": history[-1].get("timestamp"),
            "history": history
        }


# Convenience functions
def register_document_on_blockchain(
    land_record_id: int,
    ipfs_cid: str,
    owner_address: str = "0x000"
) -> Dict[str, Any]:
    """
    Register a land document on blockchain
    
    Args:
        land_record_id: Land record ID
        ipfs_cid: IPFS CID
        owner_address: Owner blockchain address
        
    Returns:
        Registration result
    """
    contract = SmartContract()
    return contract.register_land_record(
        land_record_id=land_record_id,
        ipfs_cid=ipfs_cid,
        owner_address=owner_address
    )


def verify_document_on_blockchain(
    land_record_id: int,
    ipfs_cid: str
) -> Dict[str, Any]:
    """
    Verify a land document on blockchain
    
    Args:
        land_record_id: Land record ID
        ipfs_cid: IPFS CID to verify
        
    Returns:
        Verification result
    """
    contract = SmartContract()
    return contract.verify_land_record(land_record_id, ipfs_cid) 