"""
LandGuard Merkle Tree Implementation
Efficient verification of large evidence batches
"""

import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
from pathlib import Path


class MerkleNode:
    """Node in a Merkle tree"""
    
    def __init__(self, hash_value: str, left=None, right=None, data=None):
        self.hash = hash_value
        self.left = left
        self.right = right
        self.data = data  # Leaf nodes contain actual data
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node"""
        return self.left is None and self.right is None


class MerkleTree:
    """
    Merkle Tree for efficient batch evidence verification
    Allows proving an item is in the set without revealing all items
    """
    
    def __init__(self):
        self.root = None
        self.leaves = []
        self.hash_function = hashlib.sha256
    
    def _hash(self, data: str) -> str:
        """Hash data using SHA-256"""
        return self.hash_function(data.encode('utf-8')).hexdigest()
    
    def _combine_hashes(self, left_hash: str, right_hash: str) -> str:
        """Combine two hashes"""
        combined = left_hash + right_hash
        return self._hash(combined)
    
    def build_tree(self, evidence_list: List[Dict]) -> str:
        """
        Build Merkle tree from evidence items
        
        Args:
            evidence_list: List of evidence dictionaries
        
        Returns:
            Root hash (Merkle root)
        """
        if not evidence_list:
            return None
        
        # Create leaf nodes
        self.leaves = []
        for evidence in evidence_list:
            # Hash the evidence
            evidence_json = json.dumps(evidence, sort_keys=True)
            leaf_hash = self._hash(evidence_json)
            leaf_node = MerkleNode(leaf_hash, data=evidence)
            self.leaves.append(leaf_node)
        
        # Build tree bottom-up
        self.root = self._build_tree_recursive(self.leaves)
        
        return self.root.hash
    
    def _build_tree_recursive(self, nodes: List[MerkleNode]) -> MerkleNode:
        """Recursively build tree from nodes"""
        if len(nodes) == 1:
            return nodes[0]
        
        # If odd number of nodes, duplicate last node
        if len(nodes) % 2 == 1:
            nodes.append(nodes[-1])
        
        # Build next level
        next_level = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            right = nodes[i + 1]
            
            # Combine hashes
            parent_hash = self._combine_hashes(left.hash, right.hash)
            parent = MerkleNode(parent_hash, left=left, right=right)
            next_level.append(parent)
        
        return self._build_tree_recursive(next_level)
    
    def get_proof(self, evidence_index: int) -> List[Tuple[str, str]]:
        """
        Get Merkle proof for an evidence item
        
        Args:
            evidence_index: Index of evidence in original list
        
        Returns:
            List of (hash, position) tuples forming the proof path
            Position is 'left' or 'right'
        """
        if evidence_index >= len(self.leaves):
            raise IndexError(f"Evidence index {evidence_index} out of range")
        
        proof = []
        current_nodes = self.leaves[:]
        target_index = evidence_index
        
        # Traverse from leaf to root
        while len(current_nodes) > 1:
            # Handle odd number of nodes
            if len(current_nodes) % 2 == 1:
                current_nodes.append(current_nodes[-1])
            
            # Find sibling of target node
            if target_index % 2 == 0:
                # Target is left child, sibling is right
                sibling_index = target_index + 1
                position = 'right'
            else:
                # Target is right child, sibling is left
                sibling_index = target_index - 1
                position = 'left'
            
            sibling_hash = current_nodes[sibling_index].hash
            proof.append((sibling_hash, position))
            
            # Move to next level
            next_level = []
            for i in range(0, len(current_nodes), 2):
                left = current_nodes[i]
                right = current_nodes[i + 1]
                parent_hash = self._combine_hashes(left.hash, right.hash)
                parent = MerkleNode(parent_hash, left=left, right=right)
                next_level.append(parent)
            
            current_nodes = next_level
            target_index = target_index // 2
        
        return proof
    
    def verify_proof(self, evidence: Dict, proof: List[Tuple[str, str]], 
                    root_hash: str) -> bool:
        """
        Verify that evidence is in the Merkle tree
        
        Args:
            evidence: Evidence to verify
            proof: Merkle proof (from get_proof)
            root_hash: Expected root hash
        
        Returns:
            True if evidence is in tree
        """
        # Hash the evidence
        evidence_json = json.dumps(evidence, sort_keys=True)
        current_hash = self._hash(evidence_json)
        
        # Apply proof steps
        for sibling_hash, position in proof:
            if position == 'left':
                current_hash = self._combine_hashes(sibling_hash, current_hash)
            else:
                current_hash = self._combine_hashes(current_hash, sibling_hash)
        
        # Check if we reached the root
        return current_hash == root_hash
    
    def get_tree_info(self) -> Dict[str, Any]:
        """Get information about the Merkle tree"""
        if not self.root:
            return {'empty': True}
        
        def count_nodes(node):
            if not node:
                return 0
            return 1 + count_nodes(node.left) + count_nodes(node.right)
        
        def tree_height(node):
            if not node:
                return 0
            return 1 + max(tree_height(node.left), tree_height(node.right))
        
        return {
            'root_hash': self.root.hash,
            'num_leaves': len(self.leaves),
            'total_nodes': count_nodes(self.root),
            'height': tree_height(self.root),
            'created_at': datetime.utcnow().isoformat()
        }

from pathlib import Path
class EvidenceBatchManager:
    """Manage batches of evidence using Merkle trees"""
    
    def __init__(self, storage_dir: str = 'blockchain/storage/batches'):
        self.storage_dir = Path(storage_dir) if isinstance(storage_dir, str) else storage_dir
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def create_batch(self, evidence_list: List[Dict], 
                    batch_id: str = None) -> Dict[str, Any]:
        """
        Create a Merkle tree batch for evidence items
        
        Args:
            evidence_list: List of evidence dictionaries
            batch_id: Optional batch identifier
        
        Returns:
            Batch information including root hash
        """
        if not batch_id:
            batch_id = f"BATCH_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Build Merkle tree
        tree = MerkleTree()
        root_hash = tree.build_tree(evidence_list)
        
        # Save batch info
        batch_info = {
            'batch_id': batch_id,
            'root_hash': root_hash,
            'num_items': len(evidence_list),
            'created_at': datetime.utcnow().isoformat(),
            'tree_info': tree.get_tree_info()
        }
        
        # Save batch metadata
        metadata_path = self.storage_dir / f"{batch_id}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(batch_info, f, indent=2)
        
        # Save evidence items
        evidence_path = self.storage_dir / f"{batch_id}_evidence.json"
        with open(evidence_path, 'w') as f:
            json.dump(evidence_list, f, indent=2)
        
        # Save Merkle proofs
        proofs = {}
        for i, evidence in enumerate(evidence_list):
            record_id = evidence.get('record_id', f'item_{i}')
            proof = tree.get_proof(i)
            proofs[record_id] = {
                'index': i,
                'proof': proof
            }
        
        proofs_path = self.storage_dir / f"{batch_id}_proofs.json"
        with open(proofs_path, 'w') as f:
            json.dump(proofs, f, indent=2)
        
        print(f"✅ Batch created: {batch_id}")
        print(f"   Root Hash: {root_hash}")
        print(f"   Items: {len(evidence_list)}")
        
        return batch_info
    
    def verify_evidence_in_batch(self, batch_id: str, record_id: str, 
                                 evidence: Dict) -> Dict[str, Any]:
        """
        Verify an evidence item is in a batch
        
        Args:
            batch_id: Batch identifier
            record_id: Record identifier
            evidence: Evidence to verify
        
        Returns:
            Verification result
        """
        # Load batch metadata
        metadata_path = self.storage_dir / f"{batch_id}_metadata.json"
        with open(metadata_path, 'r') as f:
            batch_info = json.load(f)
        
        # Load proofs
        proofs_path = self.storage_dir / f"{batch_id}_proofs.json"
        with open(proofs_path, 'r') as f:
            proofs = json.load(f)
        
        if record_id not in proofs:
            return {
                'is_valid': False,
                'error': f'Record {record_id} not found in batch'
            }
        
        # Get proof and verify
        proof_info = proofs[record_id]
        proof = [(h, p) for h, p in proof_info['proof']]
        root_hash = batch_info['root_hash']
        
        tree = MerkleTree()
        is_valid = tree.verify_proof(evidence, proof, root_hash)
        
        return {
            'is_valid': is_valid,
            'batch_id': batch_id,
            'record_id': record_id,
            'root_hash': root_hash,
            'proof_steps': len(proof),
            'verified_at': datetime.utcnow().isoformat(),
            'status': 'VERIFIED' if is_valid else 'INVALID'
        }
    
    def get_batch_summary(self, batch_id: str) -> Dict[str, Any]:
        """Get summary of a batch"""
        metadata_path = self.storage_dir / f"{batch_id}_metadata.json"
        
        if not metadata_path.exists():
            return {'error': 'Batch not found'}
        
        with open(metadata_path, 'r') as f:
            return json.load(f)


# Example usage
if __name__ == "__main__":
    print("🌳 LandGuard Merkle Tree Demo\n")
    
    # Create sample evidence
    evidence_batch = [
        {'record_id': 'LAND_001', 'fraud_score': 85, 'status': 'fraud'},
        {'record_id': 'LAND_002', 'fraud_score': 12, 'status': 'normal'},
        {'record_id': 'LAND_003', 'fraud_score': 67, 'status': 'suspicious'},
        {'record_id': 'LAND_004', 'fraud_score': 5, 'status': 'normal'},
        {'record_id': 'LAND_005', 'fraud_score': 92, 'status': 'fraud'}
    ]
    
    # Build Merkle tree
    print("1️⃣ Building Merkle Tree")
    print("─" * 60)
    
    tree = MerkleTree()
    root_hash = tree.build_tree(evidence_batch)
    
    print(f"✅ Tree built successfully")
    print(f"   Root Hash: {root_hash}")
    
    tree_info = tree.get_tree_info()
    print(f"   Leaves: {tree_info['num_leaves']}")
    print(f"   Total Nodes: {tree_info['total_nodes']}")
    print(f"   Height: {tree_info['height']}")
    
    # Generate proof
    print("\n2️⃣ Generating Merkle Proof")
    print("─" * 60)
    
    target_index = 2  # LAND_003
    target_evidence = evidence_batch[target_index]
    
    proof = tree.get_proof(target_index)
    print(f"Target: {target_evidence['record_id']}")
    print(f"Proof steps: {len(proof)}")
    print(f"\nProof path:")
    for i, (hash_val, position) in enumerate(proof):
        print(f"  Step {i+1}: {hash_val[:16]}... ({position})")
    
    # Verify proof
    print("\n3️⃣ Verifying Merkle Proof")
    print("─" * 60)
    
    is_valid = tree.verify_proof(target_evidence, proof, root_hash)
    print(f"Verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Test with tampered evidence
    tampered_evidence = target_evidence.copy()
    tampered_evidence['fraud_score'] = 99  # Changed!
    
    is_valid = tree.verify_proof(tampered_evidence, proof, root_hash)
    print(f"Tampered evidence: {'✅ Valid' if is_valid else '❌ Invalid (Detected!)'}")
    
    # Use batch manager
    print("\n4️⃣ Creating Evidence Batch")
    print("─" * 60)
    
 
    manager = EvidenceBatchManager()
    
    batch_info = manager.create_batch(
        evidence_batch,
        batch_id='DEMO_BATCH_001'
    )
    
    # Verify evidence in batch
    print("\n5️⃣ Verifying Evidence in Batch")
    print("─" * 60)
    
    verification = manager.verify_evidence_in_batch(
        batch_id='DEMO_BATCH_001',
        record_id='LAND_003',
        evidence=target_evidence
    )
    
    print(f"Status: {verification['status']}")
    print(f"Batch: {verification['batch_id']}")
    print(f"Record: {verification['record_id']}")
    print(f"Proof Steps: {verification['proof_steps']}")
    
    # Get batch summary
    print("\n6️⃣ Batch Summary")
    print("─" * 60)
    
    summary = manager.get_batch_summary('DEMO_BATCH_001')
    print(f"Batch ID: {summary['batch_id']}")
    print(f"Root Hash: {summary['root_hash'][:32]}...")
    print(f"Items: {summary['num_items']}")
    print(f"Created: {summary['created_at']}")
    
    print("\n✅ Merkle Tree Demo Complete!")