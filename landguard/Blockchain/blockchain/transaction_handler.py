"""
Transaction Handler
Handles blockchain transaction creation, submission, and tracking
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib
import uuid


class TransactionHandler:
    """
    Handle blockchain transactions for land records
    """
    
    def __init__(self):
        """Initialize transaction handler"""
        self.pending_transactions: List[Dict[str, Any]] = []
        self.completed_transactions: List[Dict[str, Any]] = []
        self.failed_transactions: List[Dict[str, Any]] = []
    
    def create_transaction(
        self,
        transaction_type: str,
        land_record_id: int,
        data: Dict[str, Any],
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Create a new blockchain transaction
        
        Args:
            transaction_type: Type of transaction (register, update, verify)
            land_record_id: Associated land record ID
            data: Transaction data
            priority: Transaction priority (low, normal, high)
            
        Returns:
            Transaction details
        """
        # Generate transaction ID
        tx_id = str(uuid.uuid4())
        
        # Create transaction hash
        tx_data = f"{transaction_type}:{land_record_id}:{str(data)}:{datetime.utcnow().isoformat()}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        # Create transaction
        transaction = {
            "tx_id": tx_id,
            "tx_hash": tx_hash,
            "type": transaction_type,
            "land_record_id": land_record_id,
            "data": data,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Add to pending queue
        self.pending_transactions.append(transaction)
        
        return {
            "success": True,
            "tx_id": tx_id,
            "tx_hash": tx_hash,
            "status": "pending",
            "message": f"Transaction created: {transaction_type}"
        }
    
    def submit_transaction(
        self,
        tx_id: str
    ) -> Dict[str, Any]:
        """
        Submit a pending transaction to blockchain
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            Submission result
        """
        # Find transaction
        transaction = None
        for tx in self.pending_transactions:
            if tx["tx_id"] == tx_id:
                transaction = tx
                break
        
        if not transaction:
            return {
                "success": False,
                "error": "Transaction not found"
            }
        
        # Simulate blockchain submission
        try:
            # Update transaction status
            transaction["status"] = "submitted"
            transaction["submitted_at"] = datetime.utcnow().isoformat()
            transaction["block_number"] = len(self.completed_transactions) + 1
            
            # Move to completed
            self.pending_transactions.remove(transaction)
            self.completed_transactions.append(transaction)
            
            return {
                "success": True,
                "tx_id": tx_id,
                "tx_hash": transaction["tx_hash"],
                "block_number": transaction["block_number"],
                "status": "confirmed",
                "message": "Transaction confirmed on blockchain"
            }
            
        except Exception as e:
            transaction["status"] = "failed"
            transaction["error"] = str(e)
            transaction["failed_at"] = datetime.utcnow().isoformat()
            
            self.pending_transactions.remove(transaction)
            self.failed_transactions.append(transaction)
            
            return {
                "success": False,
                "tx_id": tx_id,
                "status": "failed",
                "error": str(e)
            }
    
    def batch_submit_transactions(
        self,
        tx_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Submit multiple transactions in batch
        
        Args:
            tx_ids: List of transaction IDs
            
        Returns:
            Batch submission results
        """
        results = []
        successful = 0
        failed = 0
        
        for tx_id in tx_ids:
            result = self.submit_transaction(tx_id)
            results.append(result)
            
            if result.get("success"):
                successful += 1
            else:
                failed += 1
        
        return {
            "total": len(tx_ids),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    def get_transaction_status(
        self,
        tx_id: str
    ) -> Dict[str, Any]:
        """
        Get status of a transaction
        
        Args:
            tx_id: Transaction ID
            
        Returns:
            Transaction status
        """
        # Check pending
        for tx in self.pending_transactions:
            if tx["tx_id"] == tx_id:
                return {
                    "found": True,
                    "status": "pending",
                    "transaction": tx
                }
        
        # Check completed
        for tx in self.completed_transactions:
            if tx["tx_id"] == tx_id:
                return {
                    "found": True,
                    "status": "completed",
                    "transaction": tx
                }
        
        # Check failed
        for tx in self.failed_transactions:
            if tx["tx_id"] == tx_id:
                return {
                    "found": True,
                    "status": "failed",
                    "transaction": tx
                }
        
        return {
            "found": False,
            "error": "Transaction not found"
        }
    
    def get_pending_count(self) -> int:
        """Get count of pending transactions"""
        return len(self.pending_transactions)
    
    def get_completed_count(self) -> int:
        """Get count of completed transactions"""
        return len(self.completed_transactions)
    
    def get_failed_count(self) -> int:
        """Get count of failed transactions"""
        return len(self.failed_transactions)
    
    def get_transaction_history(
        self,
        land_record_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get transaction history
        
        Args:
            land_record_id: Filter by land record ID (optional)
            limit: Maximum number of transactions to return
            
        Returns:
            List of transactions
        """
        all_transactions = (
            self.completed_transactions + 
            self.pending_transactions + 
            self.failed_transactions
        )
        
        if land_record_id:
            all_transactions = [
                tx for tx in all_transactions
                if tx.get("land_record_id") == land_record_id
            ]
        
        # Sort by created_at descending
        all_transactions.sort(
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        
        return all_transactions[:limit]
    
    def create_and_submit(
        self,
        transaction_type: str,
        land_record_id: int,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create and immediately submit a transaction
        
        Args:
            transaction_type: Transaction type
            land_record_id: Land record ID
            data: Transaction data
            
        Returns:
            Combined result
        """
        # Create transaction
        create_result = self.create_transaction(
            transaction_type=transaction_type,
            land_record_id=land_record_id,
            data=data
        )
        
        if not create_result.get("success"):
            return create_result
        
        # Submit transaction
        tx_id = create_result.get("tx_id")
        submit_result = self.submit_transaction(tx_id)
        
        return submit_result


# Convenience functions
def register_land_transaction(
    land_record_id: int,
    ipfs_cid: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create and submit a land registration transaction
    
    Args:
        land_record_id: Land record ID
        ipfs_cid: IPFS CID
        metadata: Additional metadata
        
    Returns:
        Transaction result
    """
    handler = TransactionHandler()
    
    data = {
        "ipfs_cid": ipfs_cid,
        "action": "register"
    }
    
    if metadata:
        data["metadata"] = metadata
    
    return handler.create_and_submit(
        transaction_type="register",
        land_record_id=land_record_id,
        data=data
    )


def verify_land_transaction(
    land_record_id: int,
    ipfs_cid: str
) -> Dict[str, Any]:
    """
    Create and submit a verification transaction
    
    Args:
        land_record_id: Land record ID
        ipfs_cid: IPFS CID to verify
        
    Returns:
        Transaction result
    """
    handler = TransactionHandler()
    
    data = {
        "ipfs_cid": ipfs_cid,
        "action": "verify"
    }
    
    return handler.create_and_submit(
        transaction_type="verify",
        land_record_id=land_record_id,
        data=data
    )