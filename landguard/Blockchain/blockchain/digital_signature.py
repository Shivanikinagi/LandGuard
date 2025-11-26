"""
LandGuard Digital Signature System
RSA-based cryptographic signing for fraud reports and evidence
"""

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from typing import Dict, Tuple, Optional
from pathlib import Path
from datetime import datetime
import json
import base64


class DigitalSignatureManager:
    """Manage RSA digital signatures for fraud reports"""
    
    def __init__(self, keys_dir: str = 'blockchain/storage/signatures'):
        self.keys_dir = Path(keys_dir)
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        
        self.private_key = None
        self.public_key = None
    
    def generate_key_pair(self, key_size: int = 2048) -> Tuple[bytes, bytes]:
        """
        Generate RSA key pair
        
        Args:
            key_size: Key size in bits (2048 or 4096)
        
        Returns:
            Tuple of (private_key_pem, public_key_pem)
        """
        print(f"🔑 Generating {key_size}-bit RSA key pair...")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        # Get public key
        public_key = private_key.public_key()
        
        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Store keys
        self.private_key = private_key
        self.public_key = public_key
        
        print("✅ Key pair generated successfully")
        
        return private_pem, public_pem
    
    def save_keys(self, private_key_pem: bytes, public_key_pem: bytes,
                  key_id: str = 'landguard_main'):
        """
        Save key pair to files
        
        Args:
            private_key_pem: Private key in PEM format
            public_key_pem: Public key in PEM format
            key_id: Identifier for this key pair
        """
        private_path = self.keys_dir / f"{key_id}_private.pem"
        public_path = self.keys_dir / f"{key_id}_public.pem"
        
        # Save private key (should be kept secure!)
        with open(private_path, 'wb') as f:
            f.write(private_key_pem)
        
        # Save public key
        with open(public_path, 'wb') as f:
            f.write(public_key_pem)
        
        # Save metadata
        metadata = {
            'key_id': key_id,
            'created_at': datetime.utcnow().isoformat(),
            'algorithm': 'RSA',
            'key_size': 2048,
            'private_key_path': str(private_path),
            'public_key_path': str(public_path)
        }
        
        metadata_path = self.keys_dir / f"{key_id}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"💾 Keys saved:")
        print(f"   Private: {private_path}")
        print(f"   Public:  {public_path}")
        print(f"⚠️  IMPORTANT: Keep private key secure!")
    
    def load_keys(self, key_id: str = 'landguard_main'):
        """
        Load key pair from files
        
        Args:
            key_id: Identifier for the key pair
        """
        private_path = self.keys_dir / f"{key_id}_private.pem"
        public_path = self.keys_dir / f"{key_id}_public.pem"
        
        if not private_path.exists() or not public_path.exists():
            raise FileNotFoundError(f"Key pair not found: {key_id}")
        
        # Load private key
        with open(private_path, 'rb') as f:
            private_pem = f.read()
            self.private_key = serialization.load_pem_private_key(
                private_pem,
                password=None,
                backend=default_backend()
            )
        
        # Load public key
        with open(public_path, 'rb') as f:
            public_pem = f.read()
            self.public_key = serialization.load_pem_public_key(
                public_pem,
                backend=default_backend()
            )
        
        print(f"✅ Loaded key pair: {key_id}")
    
    def sign_data(self, data: Dict) -> str:
        """
        Create digital signature for data
        
        Args:
            data: Dictionary to sign
        
        Returns:
            Base64-encoded signature
        """
        if not self.private_key:
            raise ValueError("Private key not loaded. Call generate_key_pair() or load_keys()")
        
        # Convert data to bytes
        data_json = json.dumps(data, sort_keys=True)
        data_bytes = data_json.encode('utf-8')
        
        # Sign with private key
        signature = self.private_key.sign(
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Encode as base64 for storage
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        return signature_b64
    
    def verify_signature(self, data: Dict, signature_b64: str) -> bool:
        """
        Verify digital signature
        
        Args:
            data: Original data
            signature_b64: Base64-encoded signature
        
        Returns:
            True if signature is valid
        """
        if not self.public_key:
            raise ValueError("Public key not loaded. Call load_keys()")
        
        # Convert data to bytes
        data_json = json.dumps(data, sort_keys=True)
        data_bytes = data_json.encode('utf-8')
        
        # Decode signature
        signature = base64.b64decode(signature_b64)
        
        # Verify signature
        try:
            self.public_key.verify(
                signature,
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
    
    def sign_report(self, report: Dict, 
                   signer_name: str = 'LandGuard System',
                   signer_role: str = 'Automated Fraud Detector') -> Dict:
        """
        Sign a fraud analysis report
        
        Args:
            report: Fraud analysis report
            signer_name: Name of person/system signing
            signer_role: Role of signer
        
        Returns:
            Signed report with signature metadata
        """
        # Create signature package
        signature_data = {
            'report': report,
            'signer_name': signer_name,
            'signer_role': signer_role,
            'signed_at': datetime.utcnow().isoformat(),
            'version': '1.0'
        }
        
        # Generate signature
        signature = self.sign_data(signature_data)
        
        # Create signed report
        signed_report = {
            'report': report,
            'signature': {
                'signature_value': signature,
                'algorithm': 'RSA-PSS-SHA256',
                'signer_name': signer_name,
                'signer_role': signer_role,
                'signed_at': datetime.utcnow().isoformat(),
                'is_valid': True
            },
            'metadata': {
                'version': '1.0',
                'signed': True
            }
        }
        
        return signed_report
    
    def verify_report(self, signed_report: Dict) -> Dict[str, any]:
        """
        Verify a signed fraud report
        
        Args:
            signed_report: Signed report dictionary
        
        Returns:
            Verification result
        """
        signature_info = signed_report.get('signature', {})
        signature_value = signature_info.get('signature_value')
        
        if not signature_value:
            return {
                'is_valid': False,
                'error': 'No signature found in report'
            }
        
        # Reconstruct signature data
        signature_data = {
            'report': signed_report['report'],
            'signer_name': signature_info['signer_name'],
            'signer_role': signature_info['signer_role'],
            'signed_at': signature_info['signed_at'],
            'version': '1.0'
        }
        
        # Verify signature
        is_valid = self.verify_signature(signature_data, signature_value)
        
        return {
            'is_valid': is_valid,
            'signer_name': signature_info['signer_name'],
            'signer_role': signature_info['signer_role'],
            'signed_at': signature_info['signed_at'],
            'algorithm': signature_info['algorithm'],
            'verified_at': datetime.utcnow().isoformat(),
            'status': 'VERIFIED' if is_valid else 'INVALID'
        }
    
    def export_public_key(self, output_path: str):
        """Export public key for distribution"""
        if not self.public_key:
            raise ValueError("Public key not loaded")
        
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(output_path, 'wb') as f:
            f.write(public_pem)
        
        print(f"📤 Public key exported to: {output_path}")


class SignedEvidencePackage:
    """Create complete signed evidence packages"""
    
    def __init__(self, signature_manager: DigitalSignatureManager):
        self.sig_mgr = signature_manager
    
    def create_package(self, 
                      evidence: Dict,
                      analysis_result: Dict,
                      evidence_hash: str,
                      ipfs_cid: str = None) -> Dict:
        """
        Create a complete signed evidence package
        
        Args:
            evidence: Raw evidence data
            analysis_result: Fraud analysis result
            evidence_hash: SHA-256 hash of evidence
            ipfs_cid: IPFS Content Identifier (if uploaded)
        
        Returns:
            Signed evidence package
        """
        # Create package
        package = {
            'package_id': f"PKG_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'created_at': datetime.utcnow().isoformat(),
            'evidence': evidence,
            'analysis_result': analysis_result,
            'evidence_hash': evidence_hash,
            'ipfs_cid': ipfs_cid,
            'integrity': {
                'hash_algorithm': 'SHA-256',
                'storage_type': 'IPFS' if ipfs_cid else 'Local'
            }
        }
        
        # Sign the package
        signed_package = self.sig_mgr.sign_report(
            package,
            signer_name='LandGuard ML System',
            signer_role='Automated Fraud Detector'
        )
        
        return signed_package
    
    def verify_package(self, signed_package: Dict) -> Dict:
        """Verify a signed evidence package"""
        return self.sig_mgr.verify_report(signed_package)


# Example usage
if __name__ == "__main__":
    print("✍️  LandGuard Digital Signature Demo\n")
    
    # Initialize signature manager
    sig_mgr = DigitalSignatureManager()
    
    # Generate key pair
    print("1️⃣ Generating Key Pair")
    print("─" * 60)
    
    private_pem, public_pem = sig_mgr.generate_key_pair(key_size=2048)
    sig_mgr.save_keys(private_pem, public_pem, key_id='demo_keys')
    
    # Sign a report
    print("\n2️⃣ Signing Fraud Report")
    print("─" * 60)
    
    fraud_report = {
        'record_id': 'LAND_001',
        'is_fraudulent': True,
        'risk_score': 87.5,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    signed_report = sig_mgr.sign_report(
        fraud_report,
        signer_name='Fraud Analyst',
        signer_role='Senior Investigator'
    )
    
    print(f"✅ Report signed")
    print(f"   Signer: {signed_report['signature']['signer_name']}")
    print(f"   Signed at: {signed_report['signature']['signed_at']}")
    print(f"   Signature: {signed_report['signature']['signature_value'][:50]}...")
    
    # Verify signature
    print("\n3️⃣ Verifying Signature")
    print("─" * 60)
    
    verification = sig_mgr.verify_report(signed_report)
    print(f"Status: {verification['status']}")
    print(f"Valid: {'✅ Yes' if verification['is_valid'] else '❌ No'}")
    print(f"Verified at: {verification['verified_at']}")
    
    # Tamper detection
    print("\n4️⃣ Testing Tamper Detection")
    print("─" * 60)
    
    tampered_report = signed_report.copy()
    tampered_report['report']['risk_score'] = 10.0  # Changed!
    
    verification = sig_mgr.verify_report(tampered_report)
    print(f"Tampered report valid: {'✅ Yes' if verification['is_valid'] else '❌ No (Detected!)'}")
    
    # Complete evidence package
    print("\n5️⃣ Creating Signed Evidence Package")
    print("─" * 60)
    
    package_creator = SignedEvidencePackage(sig_mgr)
    
    evidence = {
        'documents': ['deed.pdf', 'tax_receipt.pdf'],
        'extracted_data': {'price': 5000000, 'area': 500}
    }
    
    signed_package = package_creator.create_package(
        evidence=evidence,
        analysis_result=fraud_report,
        evidence_hash='abc123def456',
        ipfs_cid='QmXXXXXX'
    )
    
    print(f"✅ Package created: {signed_package['report']['package_id']}")
    print(f"   Evidence Hash: {signed_package['report']['evidence_hash']}")
    print(f"   IPFS CID: {signed_package['report']['ipfs_cid']}")
    print(f"   Signed: {signed_package['signature']['signed_at']}")
    
    # Verify package
    verification = package_creator.verify_package(signed_package)
    print(f"\n   Verification: {verification['status']}")
    
    print("\n✅ Digital Signature Demo Complete!")