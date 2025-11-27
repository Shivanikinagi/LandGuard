# """
# LandGuard IPFS Storage Integration
# Decentralized storage for fraud evidence using Pinata IPFS gateway
# Adapted from Pied Piper project
# """

# import requests
# import json
# from typing import Dict, Any, Optional, Union
# from pathlib import Path
# from datetime import datetime
# import io


# class IPFSStorage:
#     """
#     IPFS integration for decentralized evidence storage
#     Uses Pinata gateway for easy IPFS access
#     """
    
#     def __init__(self, pinata_api_key: str = None, 
#                  pinata_secret: str = None,
#                  use_public_gateway: bool = True):
#         """
#         Initialize IPFS storage client
        
#         Args:
#             pinata_api_key: Pinata API key (optional for public gateway)
#             pinata_secret: Pinata secret key (optional)
#             use_public_gateway: Use public gateway without authentication
#         """
#         self.use_public_gateway = use_public_gateway
        
#         if use_public_gateway:
#             # Public gateway (no auth needed, but rate limited)
#             self.upload_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
#             self.gateway_url = "https://gateway.pinata.cloud/ipfs/"
#             print("ℹ️  Using public IPFS gateway (rate limited)")
#         else:
#             # Authenticated Pinata (requires API key)
#             if not pinata_api_key or not pinata_secret:
#                 raise ValueError("Pinata credentials required for authenticated mode")
            
#             self.api_key = pinata_api_key
#             self.secret = pinata_secret
#             self.upload_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
#             self.gateway_url = "https://gateway.pinata.cloud/ipfs/"
#             self.headers = {
#                 'pinata_api_key': self.api_key,
#                 'pinata_secret_api_key': self.secret
#             }
    
#     def upload_json(self, data: Dict, filename: str = None) -> Dict[str, str]:
#         """
#         Upload JSON data to IPFS
        
#         Args:
#             data: Dictionary to upload
#             filename: Optional filename for the JSON
        
#         Returns:
#             Dictionary with IPFS CID and URL
#         """
#         try:
#             # Convert to JSON
#             json_data = json.dumps(data, indent=2, ensure_ascii=False)
#             json_bytes = json_data.encode('utf-8')
            
#             # Create file-like object
#             files = {
#                 'file': (
#                     filename or 'evidence.json',
#                     io.BytesIO(json_bytes),
#                     'application/json'
#                 )
#             }
            
#             # Upload to IPFS
#             if self.use_public_gateway:
#                 # Public upload (may fail without auth)
#                 response = requests.post(
#                     self.upload_url,
#                     files=files,
#                     timeout=30
#                 )
#             else:
#                 # Authenticated upload
#                 response = requests.post(
#                     self.upload_url,
#                     files=files,
#                     headers=self.headers,
#                     timeout=30
#                 )
            
#             if response.status_code == 200:
#                 result = response.json()
#                 cid = result['IpfsHash']
                
#                 return {
#                     'success': True,
#                     'cid': cid,
#                     'url': f"{self.gateway_url}{cid}",
#                     'size_bytes': len(json_bytes),
#                     'uploaded_at': datetime.utcnow().isoformat()
#                 }
#             else:
#                 return {
#                     'success': False,
#                     'error': f"Upload failed: {response.status_code}",
#                     'message': response.text
#                 }
        
#         except Exception as e:
#             return {
#                 'success': False,
#                 'error': str(e),
#                 'fallback': 'Consider using local storage'
#             }
    
#     def upload_file(self, file_path: str) -> Dict[str, str]:
#         """
#         Upload a file to IPFS
        
#         Args:
#             file_path: Path to file to upload
        
#         Returns:
#             Dictionary with IPFS CID and URL
#         """
#         try:
#             path = Path(file_path)
            
#             if not path.exists():
#                 return {
#                     'success': False,
#                     'error': f"File not found: {file_path}"
#                 }
            
#             with open(path, 'rb') as f:
#                 files = {'file': (path.name, f, 'application/octet-stream')}
                
#                 if self.use_public_gateway:
#                     response = requests.post(
#                         self.upload_url,
#                         files=files,
#                         timeout=60
#                     )
#                 else:
#                     response = requests.post(
#                         self.upload_url,
#                         files=files,
#                         headers=self.headers,
#                         timeout=60
#                     )
            
#             if response.status_code == 200:
#                 result = response.json()
#                 cid = result['IpfsHash']
                
#                 return {
#                     'success': True,
#                     'cid': cid,
#                     'url': f"{self.gateway_url}{cid}",
#                     'filename': path.name,
#                     'size_bytes': path.stat().st_size,
#                     'uploaded_at': datetime.utcnow().isoformat()
#                 }
#             else:
#                 return {
#                     'success': False,
#                     'error': f"Upload failed: {response.status_code}",
#                     'message': response.text
#                 }
        
#         except Exception as e:
#             return {
#                 'success': False,
#                 'error': str(e)
#             }
    
#     def fetch(self, cid: str) -> Optional[bytes]:
#         """
#         Fetch content from IPFS by CID
        
#         Args:
#             cid: IPFS Content Identifier
        
#         Returns:
#             Content as bytes, or None if failed
#         """
#         try:
#             url = f"{self.gateway_url}{cid}"
#             response = requests.get(url, timeout=30)
            
#             if response.status_code == 200:
#                 return response.content
#             else:
#                 print(f"Failed to fetch {cid}: {response.status_code}")
#                 return None
        
#         except Exception as e:
#             print(f"Error fetching from IPFS: {e}")
#             return None
    
#     def fetch_json(self, cid: str) -> Optional[Dict]:
#         """
#         Fetch and parse JSON content from IPFS
        
#         Args:
#             cid: IPFS Content Identifier
        
#         Returns:
#             Parsed JSON dictionary, or None if failed
#         """
#         content = self.fetch(cid)
        
#         if content:
#             try:
#                 return json.loads(content.decode('utf-8'))
#             except Exception as e:
#                 print(f"Error parsing JSON: {e}")
#                 return None
        
#         return None
    
#     def pin_by_cid(self, cid: str) -> Dict[str, Any]:
#         """
#         Pin existing IPFS content to ensure persistence
        
#         Args:
#             cid: IPFS Content Identifier to pin
        
#         Returns:
#             Pin result dictionary
#         """
#         if self.use_public_gateway:
#             return {
#                 'success': False,
#                 'error': 'Pinning requires authenticated mode'
#             }
        
#         try:
#             pin_url = "https://api.pinata.cloud/pinning/pinByHash"
#             data = {'hashToPin': cid}
            
#             response = requests.post(
#                 pin_url,
#                 json=data,
#                 headers=self.headers,
#                 timeout=30
#             )
            
#             if response.status_code == 200:
#                 return {
#                     'success': True,
#                     'cid': cid,
#                     'pinned_at': datetime.utcnow().isoformat()
#                 }
#             else:
#                 return {
#                     'success': False,
#                     'error': f"Pin failed: {response.status_code}"
#                 }
        
#         except Exception as e:
#             return {
#                 'success': False,
#                 'error': str(e)
#             }
    
#     def get_url(self, cid: str) -> str:
#         """Get public URL for IPFS content"""
#         return f"{self.gateway_url}{cid}"
    
#     def test_connection(self) -> bool:
#         """Test IPFS gateway connectivity"""
#         try:
#             # Try to fetch a known IPFS hash
#             test_cid = "QmPZ9gcCEpqKTo6aq61g2nXGUhM4iCL3ewB6LDXZCtioEB"
#             url = f"{self.gateway_url}{test_cid}"
            
#             response = requests.get(url, timeout=10)
#             return response.status_code == 200
        
#         except:
#             return False


# class EvidenceIPFSManager:
#     """High-level manager for storing fraud evidence on IPFS"""
    
#     def __init__(self, ipfs_storage: IPFSStorage = None):
#         self.ipfs = ipfs_storage or IPFSStorage(use_public_gateway=True)
#         self.local_backup_dir = Path('blockchain/storage/ipfs_backup')
#         self.local_backup_dir.mkdir(parents=True, exist_ok=True)
    
#     def store_evidence(self, evidence: Dict, 
#                       record_id: str,
#                       evidence_hash: str) -> Dict[str, Any]:
#         """
#         Store fraud evidence on IPFS with backup
        
#         Args:
#             evidence: Evidence dictionary
#             record_id: Unique record identifier
#             evidence_hash: SHA-256 hash of evidence
        
#         Returns:
#             Storage result with IPFS CID and URLs
#         """
#         # Create evidence package
#         package = {
#             'record_id': record_id,
#             'evidence_hash': evidence_hash,
#             'evidence': evidence,
#             'stored_at': datetime.utcnow().isoformat(),
#             'version': '1.0'
#         }
        
#         # Upload to IPFS
#         print(f"📤 Uploading evidence for {record_id} to IPFS...")
#         ipfs_result = self.ipfs.upload_json(
#             package, 
#             filename=f"{record_id}_evidence.json"
#         )
        
#         # Always save local backup
#         backup_path = self.local_backup_dir / f"{record_id}.json"
#         with open(backup_path, 'w') as f:
#             json.dump(package, f, indent=2)
        
#         result = {
#             'record_id': record_id,
#             'evidence_hash': evidence_hash,
#             'ipfs_upload': ipfs_result,
#             'local_backup': str(backup_path),
#             'stored_at': datetime.utcnow().isoformat()
#         }
        
#         if ipfs_result['success']:
#             print(f"✅ Evidence stored on IPFS: {ipfs_result['cid']}")
#             print(f"🌐 URL: {ipfs_result['url']}")
#         else:
#             print(f"⚠️  IPFS upload failed, using local backup only")
#             print(f"   Error: {ipfs_result.get('error', 'Unknown')}")
        
#         return result
    
#     def retrieve_evidence(self, cid: str = None, 
#                          record_id: str = None) -> Optional[Dict]:
#         """
#         Retrieve evidence from IPFS or local backup
        
#         Args:
#             cid: IPFS Content Identifier (if available)
#             record_id: Record ID for local backup fallback
        
#         Returns:
#             Evidence package dictionary
#         """
#         # Try IPFS first
#         if cid:
#             print(f"📥 Retrieving evidence from IPFS: {cid}")
#             evidence = self.ipfs.fetch_json(cid)
            
#             if evidence:
#                 print("✅ Evidence retrieved from IPFS")
#                 return evidence
#             else:
#                 print("⚠️  IPFS retrieval failed, trying local backup...")
        
#         # Fallback to local backup
#         if record_id:
#             backup_path = self.local_backup_dir / f"{record_id}.json"
            
#             if backup_path.exists():
#                 with open(backup_path, 'r') as f:
#                     evidence = json.load(f)
#                     print("✅ Evidence retrieved from local backup")
#                     return evidence
        
#         print("❌ Evidence not found in IPFS or local backup")
#         return None
    
#     def verify_stored_evidence(self, cid: str, 
#                               expected_hash: str) -> Dict[str, Any]:
#         """
#         Verify evidence integrity from IPFS
        
#         Args:
#             cid: IPFS Content Identifier
#             expected_hash: Expected evidence hash
        
#         Returns:
#             Verification result
#         """
#         from Blockchain.blockchain.hash_manager import HashManager
        
#         # Fetch evidence
#         evidence = self.ipfs.fetch_json(cid)
        
#         if not evidence:
#             return {
#                 'is_valid': False,
#                 'error': 'Could not fetch evidence from IPFS'
#             }
        
#         # Verify hash
#         hash_mgr = HashManager()
#         actual_hash = evidence.get('evidence_hash')
#         evidence_data = evidence.get('evidence')
        
#         calculated_hash = hash_mgr.hash_data(evidence_data)
        
#         is_valid = (actual_hash == expected_hash == calculated_hash)
        
#         return {
#             'is_valid': is_valid,
#             'cid': cid,
#             'expected_hash': expected_hash,
#             'stored_hash': actual_hash,
#             'calculated_hash': calculated_hash,
#             'verified_at': datetime.utcnow().isoformat(),
#             'status': 'VERIFIED' if is_valid else 'FAILED'
#         }


# # Example usage
# if __name__ == "__main__":
#     print("🌐 LandGuard IPFS Storage Demo\n")
    
#     # Initialize IPFS storage
#     ipfs = IPFSStorage(use_public_gateway=True)
    
#     # Test connection
#     print("1️⃣ Testing IPFS Connection")
#     print("─" * 60)
#     connected = ipfs.test_connection()
#     print(f"Gateway Status: {'✅ Connected' if connected else '❌ Offline'}\n")
    
#     # Example evidence
#     evidence_data = {
#         'record_id': 'LAND_001',
#         'analysis_result': {
#             'is_fraudulent': True,
#             'risk_score': 87.5,
#             'timestamp': datetime.utcnow().isoformat()
#         },
#         'documents': [
#             'suspicious_deed.pdf',
#             'missing_tax_receipt'
#         ]
#     }
    
#     # Upload to IPFS
#     print("2️⃣ Uploading Evidence to IPFS")
#     print("─" * 60)
    
#     manager = EvidenceIPFSManager(ipfs)
    
#     # Store evidence
#     storage_result = manager.store_evidence(
#         evidence=evidence_data,
#         record_id='LAND_001',
#         evidence_hash='abc123def456...'
#     )
    
#     print(f"\n📊 Storage Result:")
#     print(f"   Record ID: {storage_result['record_id']}")
#     print(f"   Local Backup: {storage_result['local_backup']}")
    
#     if storage_result['ipfs_upload']['success']:
#         ipfs_info = storage_result['ipfs_upload']
#         print(f"   IPFS CID: {ipfs_info['cid']}")
#         print(f"   IPFS URL: {ipfs_info['url']}")
#         print(f"   Size: {ipfs_info['size_bytes']} bytes")
        
#         # Retrieve evidence
#         print("\n3️⃣ Retrieving Evidence from IPFS")
#         print("─" * 60)
        
#         retrieved = manager.retrieve_evidence(
#             cid=ipfs_info['cid'],
#             record_id='LAND_001'
#         )
        
#         if retrieved:
#             print(f"✅ Successfully retrieved evidence")
#             print(f"   Record ID: {retrieved['record_id']}")
#             print(f"   Stored At: {retrieved['stored_at']}")
#     else:
#         print(f"   ⚠️  IPFS upload failed: {storage_result['ipfs_upload']['error']}")
#         print(f"   📁 Evidence saved to local backup only")
    
#     print("\n✅ IPFS Storage Demo Complete!")

import requests
import json
from typing import Dict, Any, Optional

class IPFSStorage:
    """IPFS Storage with Pinata support"""
    
    def __init__(self, 
                 use_public_gateway: bool = False,
                 pinata_api_key: str = None,
                 pinata_api_secret: str = None):
        """
        Initialize IPFS Storage
        
        Args:
            use_public_gateway: Use public gateway (slow, rate-limited)
            pinata_api_key: Pinata API Key
            pinata_api_secret: Pinata API Secret
        """
        self.use_public_gateway = use_public_gateway
        self.pinata_api_key = "23730c498814c8e463cc"
        self.pinata_api_secret = "609832da37b5bdc97d77f963bd0481c046d07f9169ea2f7fcdfaea9067466729"

        
        # Pinata endpoints
        self.pinata_upload_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        self.pinata_json_url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
        
        # Public gateway (fallback)
        self.gateway_url = "https://gateway.pinata.cloud/ipfs"
    
    def upload_json_to_pinata(self, data: Dict) -> Dict[str, Any]:
        """
        Upload JSON data to IPFS via Pinata
        
        Args:
            data: Dictionary to upload
        
        Returns:
            Upload result with CID
        """
        if not self.pinata_api_key or not self.pinata_api_secret:
            return {
                'success': False,
                'error': 'Pinata credentials not configured'
            }
        
        headers = {
            "pinata_api_key": self.pinata_api_key,
            "pinata_api_secret": self.pinata_api_secret,
        }
        
        try:
            response = requests.post(
                self.pinata_json_url,
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                cid = result.get('IpfsHash')
                return {
                    'success': True,
                    'cid': cid,
                    'url': f"{self.gateway_url}/{cid}",
                    'status': response.status_code
                }
            else:
                return {
                    'success': False,
                    'error': f'Upload failed: {response.status_code}',
                    'details': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def retrieve_from_ipfs(self, cid: str) -> Optional[Dict]:
        """
        Retrieve JSON from IPFS
        
        Args:
            cid: Content Identifier
        
        Returns:
            Retrieved data or None
        """
        try:
            url = f"{self.gateway_url}/{cid}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return None
        
        except Exception as e:
            print(f"❌ Retrieval failed: {e}")
            return None


class EvidenceIPFSManager:
    """Evidence-specific IPFS operations"""
    
    def __init__(self, ipfs_storage: IPFSStorage):
        self.ipfs = ipfs_storage
    
    def store_evidence(self, 
                      evidence: Dict,
                      record_id: str,
                      evidence_hash: str) -> Dict[str, Any]:
        """Store evidence on IPFS"""
        
        evidence_package = {
            'record_id': record_id,
            'evidence_hash': evidence_hash,
            'data': evidence,
            'metadata': {
                'type': 'fraud_evidence',
                'source': 'landguard'
            }
        }
        
        # Try Pinata first
        if self.ipfs.pinata_api_key:
            result = self.ipfs.upload_json_to_pinata(evidence_package)
            if result['success']:
                return {
                    'ipfs_upload': {
                        'success': True,
                        'cid': result['cid'],
                        'url': result['url']
                    }
                }
        
        # Fallback to public gateway (may fail)
        return {
            'ipfs_upload': {
                'success': False,
                'cid': None,
                'url': None,
                'error': 'IPFS upload failed - no valid credentials'
            }
        }
    
    def retrieve_evidence(self, cid: str) -> Optional[Dict]:
        """Retrieve evidence from IPFS"""
        return self.ipfs.retrieve_from_ipfs(cid)