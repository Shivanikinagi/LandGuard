"""
LandGuard Phase 11: Mock KYC Integration
Works with sample data - no API required
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

from ..base import BaseIntegration, IntegrationType, ValidationError
from ..mock_data import get_mock_provider


logger = logging.getLogger(__name__)


class MockIdentityVerificationIntegration(BaseIntegration):
    """
    Mock KYC/Identity Verification using sample data
    Perfect for testing without real KYC API
    """
    
    def __init__(self):
        super().__init__(
            name="Mock Identity Verification",
            integration_type=IntegrationType.KYC,
            api_key="mock_kyc_key",
            base_url="http://mock.kyc-service.local",
            timeout=1
        )
        
        self.mock_provider = get_mock_provider()
        logger.info("Initialized Mock KYC with sample data")
    
    def authenticate(self) -> bool:
        """Mock authentication"""
        return True
    
    def test_connection(self) -> bool:
        """Mock connection test"""
        return True
    
    def get_rate_limit(self) -> Dict[str, int]:
        """Mock rate limit"""
        return {
            'limit': 999999,
            'remaining': 999999,
            'reset': 0
        }
    
    def verify_aadhar(
        self,
        aadhar_number: str,
        name: Optional[str] = None,
        consent: bool = True
    ) -> Dict[str, Any]:
        """
        Mock Aadhar verification
        
        Args:
            aadhar_number: 12-digit Aadhar number
            name: Name to verify against
            consent: User consent
        
        Returns:
            Verification result
        """
        if not consent:
            raise ValidationError(
                message="User consent required for Aadhar verification",
                integration_name=self.name
            )
        
        if not aadhar_number.isdigit() or len(aadhar_number) != 12:
            raise ValidationError(
                message="Invalid Aadhar number format (must be 12 digits)",
                integration_name=self.name,
                details={'aadhar_number': aadhar_number}
            )
        
        try:
            logger.info(f"Verifying mock Aadhar: {aadhar_number[-4:]}")
            
            result = self.mock_provider.verify_aadhar(
                aadhar_number=aadhar_number,
                name=name
            )
            
            self.record_request(success=True)
            logger.info(f"Aadhar verification {'successful' if result['verified'] else 'failed'}")
            
            return result
            
        except Exception as e:
            self.record_request(success=False, error=str(e))
            logger.error(f"Aadhar verification error: {e}")
            raise
    
    def verify_pan(
        self,
        pan_number: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mock PAN verification
        
        Args:
            pan_number: 10-character PAN
            name: Name to verify
        
        Returns:
            Verification result
        """
        if len(pan_number) != 10:
            raise ValidationError(
                message="Invalid PAN number format (must be 10 characters)",
                integration_name=self.name,
                details={'pan_number': pan_number}
            )
        
        try:
            logger.info(f"Verifying mock PAN: {pan_number}")
            
            result = self.mock_provider.verify_pan(
                pan_number=pan_number,
                name=name
            )
            
            self.record_request(success=True)
            logger.info(f"PAN verification {'successful' if result['verified'] else 'failed'}")
            
            return result
            
        except Exception as e:
            self.record_request(success=False, error=str(e))
            logger.error(f"PAN verification error: {e}")
            raise
    
    def verify_passport(
        self,
        passport_number: str,
        country: str,
        date_of_birth: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mock passport verification
        
        Returns:
            Verification result
        """
        try:
            logger.info(f"Verifying mock passport: {passport_number}")
            
            self.record_request(success=True)
            
            return {
                'verified': True,
                'name': name or "John Doe",
                'passport_number': passport_number.upper(),
                'country': country.upper(),
                'date_of_birth': date_of_birth,
                'expiry_date': '2030-12-31',
                'is_expired': False,
                'verification_id': f"PASS-VER-{hash(passport_number) % 100000:05d}",
                'verified_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.record_request(success=False, error=str(e))
            logger.error(f"Passport verification error: {e}")
            raise
    
    def verify_driving_license(
        self,
        license_number: str,
        state: str,
        date_of_birth: str
    ) -> Dict[str, Any]:
        """
        Mock driving license verification
        
        Returns:
            Verification result
        """
        try:
            logger.info(f"Verifying mock driving license: {license_number}")
            
            self.record_request(success=True)
            
            return {
                'verified': True,
                'name': "License Holder",
                'license_number': license_number.upper(),
                'state': state.upper(),
                'date_of_birth': date_of_birth,
                'valid_from': '2020-01-01',
                'valid_until': '2040-01-01',
                'is_valid': True,
                'license_classes': ['LMV', 'MCWG'],
                'verification_id': f"DL-VER-{hash(license_number) % 100000:05d}",
                'verified_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.record_request(success=False, error=str(e))
            logger.error(f"Driving license verification error: {e}")
            raise
    
    def verify_face_match(
        self,
        photo1_base64: str,
        photo2_base64: str,
        threshold: float = 0.8
    ) -> Dict[str, Any]:
        """
        Mock face matching
        
        Returns:
            Face match result
        """
        try:
            logger.info("Performing mock face match")
            
            # Simulate match based on hash similarity
            import hashlib
            hash1 = int(hashlib.md5(photo1_base64[:100].encode()).hexdigest()[:8], 16)
            hash2 = int(hashlib.md5(photo2_base64[:100].encode()).hexdigest()[:8], 16)
            
            # Mock confidence (usually high)
            confidence = 0.75 + (abs(hash1 - hash2) % 25) / 100
            
            self.record_request(success=True)
            
            return {
                'match': confidence >= threshold,
                'confidence': round(confidence, 3),
                'threshold': threshold,
                'verification_id': f"FACE-VER-{hash1 % 100000:05d}",
                'verified_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.record_request(success=False, error=str(e))
            logger.error(f"Face match error: {e}")
            raise
    
    def comprehensive_kyc(
        self,
        name: str,
        date_of_birth: str,
        aadhar_number: Optional[str] = None,
        pan_number: Optional[str] = None,
        address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mock comprehensive KYC
        
        Returns:
            KYC result with risk score
        """
        try:
            logger.info(f"Performing mock comprehensive KYC for: {name}")
            
            verifications = {}
            
            if aadhar_number:
                aadhar_result = self.verify_aadhar(aadhar_number, name)
                verifications['aadhar'] = aadhar_result['verified']
            
            if pan_number:
                pan_result = self.verify_pan(pan_number, name)
                verifications['pan'] = pan_result['verified']
            
            # Calculate mock risk score
            risk_score = 15 if all(verifications.values()) else 35
            status = 'approved' if risk_score < 30 else 'pending'
            
            self.record_request(success=True)
            
            return {
                'kyc_status': status,
                'risk_score': risk_score,
                'verifications': verifications,
                'flags': [] if status == 'approved' else ['additional_verification_needed'],
                'recommendations': ['KYC approved - low risk'] if status == 'approved' else ['Manual review recommended'],
                'kyc_id': f"KYC-{hash(name) % 1000000:06d}",
                'completed_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.record_request(success=False, error=str(e))
            logger.error(f"Comprehensive KYC error: {e}")
            raise
    
    def close(self):
        """No cleanup needed"""
        logger.info("Mock KYC closed")


# Export
__all__ = ['MockIdentityVerificationIntegration']