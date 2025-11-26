"""
LandGuard Complete Evidence Package Manager
Integrates hashing, IPFS, audit trails, signatures, and Merkle trees
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json

from hash_manager import HashManager, EvidenceIntegrityChecker
from ipfs_storage import IPFSStorage, EvidenceIPFSManager
from audit_trail import AuditTrail, AuditEventType
from digital_signature import DigitalSignatureManager, SignedEvidencePackage
from merkle_tree import MerkleTree, EvidenceBatchManager


class CompleteEvidencePackage:
    """
    Complete blockchain-backed evidence package with:
    - Cryptographic hashing
    - IPFS distributed storage
    - Immutable audit trail
    - Digital signatures
    - Merkle tree verification
    """
    
    def __init__(self, 
                 storage_dir: str = 'blockchain/storage',
                 use_ipfs: bool = True):
        """
        Initialize complete evidence system
        
        Args:
            storage_dir: Base directory for blockchain storage
            use_ipfs: Enable IPFS storage
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.hash_manager = HashManager(
            str(self.storage_dir / 'hashes')
        )
        
        self.audit_trail = AuditTrail(
            str(self.storage_dir / 'audit_logs')
        )
        
        self.signature_manager = DigitalSignatureManager(
            str(self.storage_dir / 'signatures')
        )
        
        self.batch_manager = EvidenceBatchManager(
            str(self.storage_dir / 'batches')
        )
        
        # IPFS (optional)
        if use_ipfs:
            self.ipfs_manager = EvidenceIPFSManager(
                IPFSStorage(use_public_gateway=True)
            )
        else:
            self.ipfs_manager = None
        
        # Initialize signature keys if not exist
        self._initialize_keys()
        
        print("✅ Complete Evidence System Initialized")
    
    def _initialize_keys(self):
        """Initialize RSA keys if they don't exist"""
        try:
            self.signature_manager.load_keys('landguard_main')
        except FileNotFoundError:
            print("🔑 Generating new signature keys...")
            private_pem, public_pem = self.signature_manager.generate_key_pair()
            self.signature_manager.save_keys(
                private_pem, public_pem, 
                key_id='landguard_main'
            )
    
    def store_fraud_evidence(self, 
                            record_id: str,
                            analysis_result: Dict,
                            ml_predictions: Dict = None,
                            documents: List[str] = None,
                            user_id: str = 'system') -> Dict[str, Any]:
        """
        Store complete fraud evidence with all blockchain features
        
        Args:
            record_id: Unique record identifier
            analysis_result: Fraud analysis result
            ml_predictions: ML model predictions (optional)
            documents: List of document paths (optional)
            user_id: User storing the evidence
        
        Returns:
            Complete storage result with all verification data
        """
        start_time = datetime.utcnow()
        
        print(f"\n{'='*70}")
        print(f"📦 Storing Evidence for Record: {record_id}")
        print(f"{'='*70}")
        
        # Step 1: Log analysis started
        self.audit_trail.log_analysis_started(
            record_id=record_id,
            input_file='fraud_analysis',
            user_id=user_id
        )
        
        # Step 2: Create evidence package
        evidence = {
            'record_id': record_id,
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_result': analysis_result,
            'ml_predictions': ml_predictions or {},
            'documents': documents or [],
            'metadata': {
                'version': '1.0',
                'user_id': user_id
            }
        }
        
        # Step 3: Calculate evidence hash
        print("\n1️⃣ Calculating Evidence Hash...")
        evidence_hash = self.hash_manager.hash_data(evidence)
        print(f"   ✅ Hash: {evidence_hash[:32]}...")
        
        # Save hash record
        self.hash_manager.save_hash_record(
            record_id=record_id,
            hash_value=evidence_hash,
            metadata={'type': 'fraud_evidence'}
        )
        
        # Step 4: Upload to IPFS (if enabled)
        ipfs_cid = None
        ipfs_url = None
        
        if self.ipfs_manager:
            print("\n2️⃣ Uploading to IPFS...")
            ipfs_result = self.ipfs_manager.store_evidence(
                evidence=evidence,
                record_id=record_id,
                evidence_hash=evidence_hash
            )
            
            if ipfs_result['ipfs_upload']['success']:
                ipfs_cid = ipfs_result['ipfs_upload']['cid']
                ipfs_url = ipfs_result['ipfs_upload']['url']
                print(f"   ✅ IPFS CID: {ipfs_cid}")
            else:
                print(f"   ⚠️  IPFS upload failed, using local backup")
        
        # Step 5: Log evidence stored
        self.audit_trail.log_evidence_stored(
            record_id=record_id,
            evidence_hash=evidence_hash,
            ipfs_cid=ipfs_cid,
            storage_location='IPFS+Local' if ipfs_cid else 'Local',
            user_id=user_id
        )
        
        # Step 6: Create digital signature
        print("\n3️⃣ Creating Digital Signature...")
        signed_package = self.signature_manager.sign_report(
            evidence,
            signer_name='LandGuard System',
            signer_role='Automated Fraud Detector'
        )
        print(f"   ✅ Signature created")
        
        # Step 7: Log fraud detection (if fraud found)
        is_fraudulent = analysis_result.get('is_fraudulent', False)
        risk_score = analysis_result.get('risk_score', 0)
        
        if is_fraudulent:
            self.audit_trail.log_fraud_detected(
                record_id=record_id,
                risk_score=risk_score,
                evidence_hash=evidence_hash,
                user_id=user_id
            )
        
        # Step 8: Complete audit log
        duration = (datetime.utcnow() - start_time).total_seconds()
        self.audit_trail.log_analysis_completed(
            record_id=record_id,
            result=analysis_result,
            duration_seconds=duration,
            user_id=user_id
        )
        
        # Step 9: Create complete package
        print("\n4️⃣ Creating Complete Package...")
        complete_package = {
            'record_id': record_id,
            'evidence': evidence,
            'signed_package': signed_package,
            'integrity': {
                'evidence_hash': evidence_hash,
                'ipfs_cid': ipfs_cid,
                'ipfs_url': ipfs_url,
                'signature': signed_package['signature']['signature_value'][:64] + '...',
                'signature_algorithm': signed_package['signature']['algorithm']
            },
            'storage': {
                'local_backup': str(self.storage_dir / 'evidence' / f"{record_id}.json"),
                'ipfs': ipfs_cid is not None,
                'audit_logged': True,
                'signed': True
            },
            'timestamps': {
                'stored_at': datetime.utcnow().isoformat(),
                'duration_seconds': duration
            }
        }
        
        # Save complete package locally
        evidence_dir = self.storage_dir / 'evidence'
        evidence_dir.mkdir(exist_ok=True)
        
        package_path = evidence_dir / f"{record_id}_complete.json"
        with open(package_path, 'w') as f:
            json.dump(complete_package, f, indent=2)
        
        print(f"\n✅ Evidence Package Complete!")
        print(f"   Record ID: {record_id}")
        print(f"   Hash: {evidence_hash[:32]}...")
        if ipfs_cid:
            print(f"   IPFS: {ipfs_cid}")
        print(f"   Signed: Yes")
        print(f"   Audit Logged: Yes")
        print(f"   Package: {package_path}")
        
        return complete_package
    
    def verify_evidence(self, 
                       record_id: str = None,
                       evidence_hash: str = None,
                       ipfs_cid: str = None) -> Dict[str, Any]:
        """
        Verify evidence integrity from any source
        
        Args:
            record_id: Record identifier
            evidence_hash: Expected hash
            ipfs_cid: IPFS Content Identifier
        
        Returns:
            Comprehensive verification result
        """
        print(f"\n{'='*70}")
        print(f"🔍 Verifying Evidence")
        print(f"{'='*70}")
        
        verification_result = {
            'verified_at': datetime.utcnow().isoformat(),
            'checks': {}
        }
        
        # Load evidence
        evidence = None
        
        if record_id:
            # Try loading from local storage
            package_path = self.storage_dir / 'evidence' / f"{record_id}_complete.json"
            if package_path.exists():
                with open(package_path, 'r') as f:
                    package = json.load(f)
                    evidence = package['evidence']
                    verification_result['source'] = 'local'
        
        if not evidence and ipfs_cid and self.ipfs_manager:
            # Try loading from IPFS
            ipfs_data = self.ipfs_manager.retrieve_evidence(cid=ipfs_cid)
            if ipfs_data:
                evidence = ipfs_data.get('evidence')
                verification_result['source'] = 'ipfs'
        
        if not evidence:
            return {
                'is_valid': False,
                'error': 'Evidence not found'
            }
        
        # Check 1: Hash integrity
        print("\n1️⃣ Checking Hash Integrity...")
        checker = EvidenceIntegrityChecker(self.hash_manager)
        
        if evidence_hash:
            hash_check = checker.check_evidence(evidence, evidence_hash)
            verification_result['checks']['hash'] = hash_check
            print(f"   {'✅' if hash_check['is_valid'] else '❌'} Hash: {hash_check['status']}")
        
        # Check 2: Signature validity
        print("\n2️⃣ Checking Digital Signature...")
        if package_path.exists():
            with open(package_path, 'r') as f:
                package = json.load(f)
                signed_package = package['signed_package']
            
            sig_check = self.signature_manager.verify_report(signed_package)
            verification_result['checks']['signature'] = sig_check
            print(f"   {'✅' if sig_check['is_valid'] else '❌'} Signature: {sig_check['status']}")
        
        # Check 3: Audit trail consistency
        print("\n3️⃣ Checking Audit Trail...")
        if record_id:
            history = self.audit_trail.get_record_history(record_id)
            verification_result['checks']['audit'] = {
                'entries_found': len(history),
                'is_complete': len(history) >= 2  # At least start and complete
            }
            print(f"   ✅ Audit Entries: {len(history)}")
        
        # Check 4: Audit trail integrity
        print("\n4️⃣ Verifying Audit Trail Integrity...")
        audit_integrity = self.audit_trail.verify_integrity()
        verification_result['checks']['audit_integrity'] = audit_integrity
        print(f"   {'✅' if audit_integrity['is_valid'] else '❌'} Integrity: {audit_integrity['status']}")
        
        # Overall verdict
        all_checks_passed = all(
            check.get('is_valid', True) 
            for check in verification_result['checks'].values()
        )
        
        verification_result['is_valid'] = all_checks_passed
        verification_result['status'] = 'VERIFIED' if all_checks_passed else 'FAILED'
        
        print(f"\n{'='*70}")
        print(f"{'✅' if all_checks_passed else '❌'} Overall Status: {verification_result['status']}")
        print(f"{'='*70}")
        
        return verification_result
    
    def create_evidence_batch(self, 
                             evidence_items: List[Dict],
                             batch_id: str = None) -> Dict[str, Any]:
        """
        Create a Merkle tree batch for multiple evidence items
        
        Args:
            evidence_items: List of evidence packages
            batch_id: Optional batch identifier
        
        Returns:
            Batch creation result
        """
        print(f"\n{'='*70}")
        print(f"🌳 Creating Evidence Batch")
        print(f"{'='*70}")
        
        # Create Merkle tree batch
        batch_info = self.batch_manager.create_batch(evidence_items, batch_id)
        
        # Log batch creation
        self.audit_trail.log_event(
            event_type=AuditEventType.SYSTEM_EVENT,
            record_id=batch_info['batch_id'],
            details={
                'action': 'Evidence batch created',
                'num_items': len(evidence_items),
                'root_hash': batch_info['root_hash']
            },
            user_id='system'
        )
        
        return batch_info
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            'audit_trail': self.audit_trail.get_statistics(),
            'storage_dir': str(self.storage_dir),
            'ipfs_enabled': self.ipfs_manager is not None,
            'components': {
                'hash_manager': 'active',
                'audit_trail': 'active',
                'signature_manager': 'active',
                'batch_manager': 'active',
                'ipfs_manager': 'active' if self.ipfs_manager else 'disabled'
            }
        }


# Example usage
if __name__ == "__main__":
    print("📦 LandGuard Complete Evidence Package Demo\n")
    
    # Initialize system
    evidence_system = CompleteEvidencePackage(
        storage_dir='blockchain/storage',
        use_ipfs=True
    )
    
    # Example fraud analysis result
    analysis_result = {
        'is_fraudulent': True,
        'risk_score': 87.5,
        'confidence': 0.92,
        'fraud_indicators': [
            'Price deviation > 50%',
            'Missing critical documents',
            'Seller-buyer same name'
        ]
    }
    
    ml_predictions = {
        'anomaly_score': 0.89,
        'classifier_probability': 0.92,
        'pattern_matches': 3
    }
    
    # Store evidence
    package = evidence_system.store_fraud_evidence(
        record_id='LAND_DEMO_001',
        analysis_result=analysis_result,
        ml_predictions=ml_predictions,
        documents=['deed.pdf', 'tax_receipt.pdf'],
        user_id='demo_analyst'
    )
    
    # Verify evidence
    verification = evidence_system.verify_evidence(
        record_id='LAND_DEMO_001',
        evidence_hash=package['integrity']['evidence_hash']
    )
    
    # Get statistics
    print(f"\n{'='*70}")
    print(f"📊 System Statistics")
    print(f"{'='*70}")
    
    stats = evidence_system.get_system_statistics()
    print(f"\nAudit Trail:")
    print(f"   Total Entries: {stats['audit_trail']['total_entries']}")
    print(f"   Unique Records: {stats['audit_trail']['unique_records']}")
    
    print(f"\nComponents:")
    for component, status in stats['components'].items():
        print(f"   {component:20s}: {status}")
    
    print("\n✅ Complete Evidence Package Demo Complete!")