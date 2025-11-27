"""
LandGuard Phase 11: Mock Land Registry Integration
Works with sample data - no API required
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import logging

from ..base import BaseIntegration, IntegrationType, APIError
from ..mock_data import get_mock_provider


logger = logging.getLogger(__name__)


class MockLandRegistryIntegration(BaseIntegration):
    """
    Mock Land Registry Integration using sample data
    Perfect for testing and development without real API
    """
    
    def __init__(self):
        super().__init__(
            name="Mock Government Land Registry",
            integration_type=IntegrationType.GOVERNMENT,
            api_key="mock_key",
            base_url="http://mock.landregistry.local",
            timeout=1
        )
        
        self.mock_provider = get_mock_provider()
        logger.info("Initialized Mock Land Registry with sample data")
    
    def authenticate(self) -> bool:
        """Mock authentication always succeeds"""
        logger.info("Mock authentication successful")
        return True
    
    def test_connection(self) -> bool:
        """Mock connection test always succeeds"""
        logger.info("Mock connection test successful")
        return True
    
    def get_rate_limit(self) -> Dict[str, int]:
        """Mock rate limit - unlimited"""
        return {
            'limit': 999999,
            'remaining': 999999,
            'reset': 0
        }
    
    def get_property_details(
        self,
        survey_number: str,
        district: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Fetch mock property details
        
        Args:
            survey_number: Survey/plot number
            district: District name
            state: State name
        
        Returns:
            Property details from mock data
        """
        try:
            logger.info(f"Fetching mock property: {survey_number}, {district}, {state}")
            
            result = self.mock_provider.get_property_details(
                survey_number=survey_number,
                district=district,
                state=state
            )
            
            self.record_request(success=True)
            logger.info(f"Successfully fetched property for {survey_number}")
            
            return result
            
        except Exception as e:
            self.record_request(success=False, error=str(e))
            logger.error(f"Failed to fetch property details: {e}")
            raise APIError(
                message=f"Failed to fetch property details: {e}",
                integration_name=self.name,
                details={'survey_number': survey_number, 'district': district}
            )
    
    def get_ownership_history(
        self,
        survey_number: str,
        district: str,
        state: str
    ) -> List[Dict[str, Any]]:
        """
        Get mock ownership history
        
        Returns:
            List of ownership records
        """
        try:
            logger.info(f"Fetching mock ownership history: {survey_number}")
            
            history = self.mock_provider.get_ownership_history(
                survey_number=survey_number,
                district=district,
                state=state
            )
            
            self.record_request(success=True)
            logger.info(f"Retrieved {len(history)} ownership records")
            
            return history
            
        except Exception as e:
            self.record_request(success=False, error=str(e))
            logger.error(f"Failed to fetch ownership history: {e}")
            raise APIError(
                message=f"Failed to fetch ownership history: {e}",
                integration_name=self.name
            )
    
    def check_encumbrances(
        self,
        survey_number: str,
        district: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Check mock encumbrances
        
        Returns:
            Encumbrance certificate data
        """
        try:
            logger.info(f"Checking mock encumbrances: {survey_number}")
            
            result = self.mock_provider.get_encumbrances(
                survey_number=survey_number,
                district=district,
                state=state
            )
            
            self.record_request(success=True)
            logger.info(f"Found {result['count']} encumbrance(s)")
            
            return result
            
        except Exception as e:
            self.record_request(success=False, error=str(e))
            logger.error(f"Failed to check encumbrances: {e}")
            raise APIError(
                message=f"Failed to check encumbrances: {e}",
                integration_name=self.name
            )
    
    def verify_document(
        self,
        document_number: str,
        registration_date: str,
        district: str
    ) -> Dict[str, Any]:
        """
        Mock document verification
        
        Returns:
            Document verification result
        """
        try:
            logger.info(f"Verifying mock document: {document_number}")
            
            self.record_request(success=True)
            
            # Return mock verification
            return {
                'is_valid': True,
                'document_number': document_number,
                'registration_date': registration_date,
                'document_type': 'Sale Deed',
                'parties': ['Seller Name', 'Buyer Name'],
                'property_details': {
                    'survey_number': '123/4',
                    'district': district
                },
                'verified_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.record_request(success=False, error=str(e))
            logger.error(f"Failed to verify document: {e}")
            raise APIError(
                message=f"Failed to verify document: {e}",
                integration_name=self.name
            )
    
    def search_by_owner(
        self,
        owner_name: str,
        district: Optional[str] = None,
        state: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Mock search by owner
        
        Returns:
            List of properties
        """
        try:
            logger.info(f"Searching mock properties for owner: {owner_name}")
            
            # Return 1-3 mock properties
            import random
            num_props = random.randint(1, 3)
            
            properties = []
            for i in range(num_props):
                properties.append({
                    'survey_number': f"{random.randint(100, 999)}/{random.randint(1, 20)}",
                    'district': district or random.choice(['Mumbai', 'Pune', 'Nashik']),
                    'state': state or 'Maharashtra',
                    'area': random.randint(500, 3000),
                    'property_type': random.choice(['residential', 'commercial']),
                    'ownership_since': f"{random.randint(2010, 2023)}-{random.randint(1, 12):02d}-01"
                })
            
            self.record_request(success=True)
            logger.info(f"Found {len(properties)} propertie(s) for {owner_name}")
            
            return properties
            
        except Exception as e:
            self.record_request(success=False, error=str(e))
            logger.error(f"Failed to search by owner: {e}")
            raise APIError(
                message=f"Failed to search by owner: {e}",
                integration_name=self.name
            )
    
    def close(self):
        """No cleanup needed for mock"""
        logger.info("Mock Land Registry closed")


# Export
__all__ = ['MockLandRegistryIntegration']