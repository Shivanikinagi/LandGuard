"""
LandGuard Phase 11: Mock Data Provider
Provides realistic sample data for testing without real APIs
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone
import random
import hashlib


class MockDataProvider:
    """
    Provides mock/sample data for all integrations
    Simulates realistic government, KYC, and valuation data
    """
    
    # Sample data pools
    DISTRICTS = ["Mumbai", "Pune", "Nashik", "Nagpur", "Thane", "Aurangabad"]
    STATES = ["Maharashtra", "Karnataka", "Gujarat", "Tamil Nadu", "Delhi"]
    
    OWNER_NAMES = [
        "Rajesh Kumar", "Priya Sharma", "Amit Patel", "Sunita Desai",
        "Vijay Singh", "Anjali Mehta", "Rahul Verma", "Deepika Iyer",
        "Arjun Nair", "Pooja Reddy", "Sanjay Gupta", "Kavita Joshi"
    ]
    
    PROPERTY_TYPES = ["residential", "commercial", "industrial", "agricultural"]
    
    ENCUMBRANCE_TYPES = ["mortgage", "loan", "lien", "easement", "covenant"]
    
    BANKS = ["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "PNB", "Kotak Mahindra"]
    
    STREETS = ["MG Road", "Main Street", "Park Avenue", "Station Road", "Mall Road"]
    
    def __init__(self, seed: int = 42):
        """Initialize with seed for reproducible data"""
        random.seed(seed)
    
    def _generate_survey_number(self) -> str:
        """Generate realistic survey number"""
        return f"{random.randint(1, 999)}/{random.randint(1, 20)}"
    
    def _generate_document_number(self) -> str:
        """Generate document registration number"""
        year = random.randint(2015, 2024)
        seq = random.randint(1000, 9999)
        return f"DOC/{year}/{seq}"
    
    def _generate_aadhar(self) -> str:
        """Generate mock Aadhar number"""
        return ''.join([str(random.randint(0, 9)) for _ in range(12)])
    
    def _generate_pan(self) -> str:
        """Generate mock PAN number"""
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return (
            ''.join(random.choices(letters, k=5)) +
            ''.join([str(random.randint(0, 9)) for _ in range(4)]) +
            random.choice(letters)
        )
    
    def get_property_details(
        self,
        survey_number: str,
        district: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Mock land registry property details
        """
        # Use inputs to seed random for consistency
        seed_str = f"{survey_number}{district}{state}"
        seed_val = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        random.seed(seed_val)
        
        owner = random.choice(self.OWNER_NAMES)
        prop_type = random.choice(self.PROPERTY_TYPES)
        area = random.randint(500, 5000)
        
        # Generate encumbrances (30% chance)
        encumbrances = []
        if random.random() < 0.3:
            num_enc = random.randint(1, 2)
            for _ in range(num_enc):
                encumbrances.append({
                    'type': random.choice(self.ENCUMBRANCE_TYPES),
                    'amount': random.randint(500000, 5000000),
                    'creditor': random.choice(self.BANKS),
                    'date': (datetime.now() - timedelta(days=random.randint(30, 730))).strftime('%Y-%m-%d'),
                    'status': random.choice(['active', 'cleared']),
                    'document_number': self._generate_document_number()
                })
        
        return {
            'success': True,
            'data': {
                'survey_number': survey_number,
                'district': district,
                'state': state,
                'area': area,
                'area_unit': 'sqft',
                'property_type': prop_type,
                'current_owner': owner,
                'owner_since': (datetime.now() - timedelta(days=random.randint(365, 3650))).strftime('%Y-%m-%d'),
                'registration_date': (datetime.now() - timedelta(days=random.randint(730, 7300))).strftime('%Y-%m-%d'),
                'document_number': self._generate_document_number(),
                'market_value': area * random.randint(3000, 8000),
                'encumbrances': encumbrances,
                'last_updated': datetime.now(timezone.utc).isoformat()
            },
            'source': 'mock_government_registry',
            'verified': True
        }
    
    def get_ownership_history(
        self,
        survey_number: str,
        district: str,
        state: str
    ) -> List[Dict[str, Any]]:
        """Mock ownership history"""
        seed_str = f"{survey_number}{district}{state}history"
        seed_val = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        random.seed(seed_val)
        
        num_owners = random.randint(2, 5)
        history = []
        
        current_date = datetime.now()
        for i in range(num_owners):
            from_date = current_date - timedelta(days=random.randint(730, 3650))
            to_date = current_date if i == 0 else from_date + timedelta(days=random.randint(365, 2555))
            
            history.append({
                'owner_name': random.choice(self.OWNER_NAMES),
                'ownership_from': from_date.strftime('%Y-%m-%d'),
                'ownership_to': to_date.strftime('%Y-%m-%d') if i > 0 else 'Present',
                'document_number': self._generate_document_number(),
                'registration_date': from_date.strftime('%Y-%m-%d'),
                'transaction_type': random.choice(['sale', 'inheritance', 'gift', 'partition']),
                'sale_value': random.randint(1000000, 10000000) if random.random() > 0.3 else None
            })
            
            current_date = from_date
        
        return list(reversed(history))
    
    def get_encumbrances(
        self,
        survey_number: str,
        district: str,
        state: str
    ) -> Dict[str, Any]:
        """Mock encumbrance certificate"""
        seed_str = f"{survey_number}{district}{state}enc"
        seed_val = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        random.seed(seed_val)
        
        has_enc = random.random() < 0.4
        
        encumbrances = []
        if has_enc:
            num_enc = random.randint(1, 3)
            for _ in range(num_enc):
                encumbrances.append({
                    'type': random.choice(self.ENCUMBRANCE_TYPES),
                    'amount': random.randint(500000, 5000000),
                    'creditor': random.choice(self.BANKS),
                    'date': (datetime.now() - timedelta(days=random.randint(30, 1095))).strftime('%Y-%m-%d'),
                    'status': random.choice(['active', 'cleared']),
                    'document_number': self._generate_document_number()
                })
        
        return {
            'has_encumbrances': has_enc,
            'count': len(encumbrances),
            'encumbrances': encumbrances,
            'certificate_number': f"EC/{random.randint(2024, 2025)}/{random.randint(1000, 9999)}",
            'issued_date': datetime.now().strftime('%Y-%m-%d'),
            'valid_until': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        }
    
    def verify_aadhar(
        self,
        aadhar_number: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mock Aadhar verification"""
        seed_val = int(hashlib.md5(aadhar_number.encode()).hexdigest()[:8], 16)
        random.seed(seed_val)
        
        verified_name = name if name else random.choice(self.OWNER_NAMES)
        
        return {
            'verified': random.random() > 0.1,  # 90% success rate
            'name': verified_name,
            'date_of_birth': f"{random.randint(1960, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            'gender': random.choice(['Male', 'Female']),
            'address': f"{random.randint(1, 999)} {random.choice(self.STREETS)}, {random.choice(self.DISTRICTS)}",
            'masked_aadhar': f"XXXX-XXXX-{aadhar_number[-4:]}",
            'verification_id': f"VER-{random.randint(10000, 99999)}",
            'verified_at': datetime.now(timezone.utc).isoformat(),
            'confidence_score': random.randint(85, 100)
        }
    
    def verify_pan(
        self,
        pan_number: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mock PAN verification"""
        seed_val = int(hashlib.md5(pan_number.encode()).hexdigest()[:8], 16)
        random.seed(seed_val)
        
        verified_name = name if name else random.choice(self.OWNER_NAMES)
        
        return {
            'verified': random.random() > 0.05,  # 95% success rate
            'name': verified_name,
            'date_of_birth': f"{random.randint(1960, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            'pan_number': pan_number.upper(),
            'status': random.choice(['Valid', 'Active']),
            'verification_id': f"PAN-VER-{random.randint(10000, 99999)}",
            'verified_at': datetime.now(timezone.utc).isoformat()
        }
    
    def estimate_property_value(
        self,
        address: str,
        area_sqft: float,
        property_type: str
    ) -> Dict[str, Any]:
        """Mock property valuation"""
        seed_val = int(hashlib.md5(address.encode()).hexdigest()[:8], 16)
        random.seed(seed_val)
        
        # Base price per sqft varies by property type
        base_prices = {
            'residential': random.randint(3000, 8000),
            'commercial': random.randint(5000, 15000),
            'industrial': random.randint(2000, 6000),
            'agricultural': random.randint(500, 2000)
        }
        
        base_price = base_prices.get(property_type, 5000)
        estimated_value = int(area_sqft * base_price)
        
        # Add some variance
        variance = random.uniform(0.85, 1.15)
        estimated_value = int(estimated_value * variance)
        
        return {
            'estimated_value': estimated_value,
            'currency': 'INR',
            'value_range': {
                'low': int(estimated_value * 0.9),
                'high': int(estimated_value * 1.1)
            },
            'confidence_score': random.randint(75, 95),
            'price_per_sqft': int(estimated_value / area_sqft),
            'valuation_date': datetime.now(timezone.utc).isoformat(),
            'factors': {
                'location_score': random.randint(6, 10),
                'market_trend': random.choice(['rising', 'stable', 'declining']),
                'amenities_score': random.randint(5, 10),
                'age_factor': random.uniform(0.8, 1.0)
            },
            'methodology': 'comparative_market_analysis'
        }
    
    def get_comparable_sales(
        self,
        address: str,
        radius_km: float = 2.0,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Mock comparable sales"""
        seed_val = int(hashlib.md5(address.encode()).hexdigest()[:8], 16)
        random.seed(seed_val)
        
        num_results = min(random.randint(5, 15), max_results)
        comparables = []
        
        for i in range(num_results):
            area = random.randint(800, 3000)
            price_per_sqft = random.randint(3000, 8000)
            
            comparables.append({
                'address': f"{random.randint(1, 999)} {random.choice(self.STREETS)}, {random.choice(self.DISTRICTS)}",
                'distance_km': round(random.uniform(0.1, radius_km), 2),
                'sale_price': area * price_per_sqft,
                'sale_date': (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d'),
                'area_sqft': area,
                'price_per_sqft': price_per_sqft,
                'property_type': random.choice(['residential', 'commercial']),
                'bedrooms': random.randint(1, 4) if random.random() > 0.5 else None,
                'bathrooms': random.randint(1, 3) if random.random() > 0.5 else None,
                'year_built': random.randint(1990, 2023),
                'similarity_score': random.randint(70, 95)
            })
        
        # Sort by similarity score
        comparables.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return comparables
    
    def get_market_trends(
        self,
        location: str,
        property_type: str
    ) -> Dict[str, Any]:
        """Mock market trends"""
        seed_val = int(hashlib.md5(f"{location}{property_type}".encode()).hexdigest()[:8], 16)
        random.seed(seed_val)
        
        avg_price = random.randint(3000000, 10000000)
        
        # Generate historical data (last 12 months)
        historical = []
        base_price = avg_price * 0.85
        for i in range(12):
            month_date = datetime.now() - timedelta(days=30 * (11 - i))
            price = base_price * (1 + (i * 0.015))  # Gradual increase
            historical.append({
                'month': month_date.strftime('%Y-%m'),
                'average_price': int(price),
                'transactions': random.randint(50, 200)
            })
        
        return {
            'location': location,
            'property_type': property_type,
            'average_price': avg_price,
            'median_price': int(avg_price * 0.95),
            'price_trend': random.choice(['up', 'stable', 'down']),
            'yoy_change_percent': round(random.uniform(-5, 15), 2),
            'mom_change_percent': round(random.uniform(-2, 3), 2),
            'inventory_level': random.choice(['low', 'medium', 'high']),
            'days_on_market': random.randint(30, 120),
            'historical_data': historical,
            'forecast': {
                'next_quarter': int(avg_price * random.uniform(1.02, 1.08)),
                'next_year': int(avg_price * random.uniform(1.05, 1.15))
            }
        }


# Global instance
_mock_provider = MockDataProvider()


def get_mock_provider() -> MockDataProvider:
    """Get the global mock data provider"""
    return _mock_provider


# Export
__all__ = ['MockDataProvider', 'get_mock_provider']