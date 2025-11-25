"""
LandGuard ML Feature Engineering
Extracts machine learning features from land records for fraud detection
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Any
import re


class FeatureEngineer:
    """Extract ML features from land records"""
    
    def __init__(self):
        self.feature_names = []
        
    def extract_features(self, record: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract all ML features from a land record
        
        Args:
            record: Land record dictionary with fields like:
                - owner_name, survey_number, area, price, 
                - registration_date, documents, etc.
        
        Returns:
            Dictionary of feature_name -> feature_value
        """
        features = {}
        
        # Price-based features
        features.update(self._price_features(record))
        
        # Document-based features
        features.update(self._document_features(record))
        
        # Temporal features
        features.update(self._temporal_features(record))
        
        # Owner features
        features.update(self._owner_features(record))
        
        # Area/Survey features
        features.update(self._survey_features(record))
        
        # Transaction features
        features.update(self._transaction_features(record))
        
        self.feature_names = list(features.keys())
        return features
    
    def _price_features(self, record: Dict) -> Dict[str, float]:
        """Extract price-related features"""
        features = {}
        
        price = record.get('price', 0) or 0
        area = record.get('area', 0) or 0
        market_value = record.get('market_value', 0) or 0
        
        # Price per unit area
        features['price_per_sqm'] = price / area if area > 0 else 0
        
        # Price deviation from market value
        if market_value > 0:
            features['price_deviation_ratio'] = abs(price - market_value) / market_value
            features['price_below_market'] = 1.0 if price < market_value * 0.7 else 0.0
            features['price_above_market'] = 1.0 if price > market_value * 1.5 else 0.0
        else:
            features['price_deviation_ratio'] = 0.0
            features['price_below_market'] = 0.0
            features['price_above_market'] = 0.0
        
        # Round number detection (suspicious)
        features['is_round_price'] = 1.0 if price % 100000 == 0 else 0.0
        
        # Price magnitude (log scale)
        features['price_magnitude'] = np.log10(price + 1)
        
        return features
    
    def _document_features(self, record: Dict) -> Dict[str, float]:
        """Extract document-related features"""
        features = {}
        
        documents = record.get('documents', [])
        
        # Document counts
        features['num_documents'] = len(documents)
        features['has_sale_deed'] = 1.0 if any('sale' in str(d).lower() for d in documents) else 0.0
        features['has_title_deed'] = 1.0 if any('title' in str(d).lower() for d in documents) else 0.0
        features['has_tax_receipt'] = 1.0 if any('tax' in str(d).lower() for d in documents) else 0.0
        
        # Missing critical documents
        critical_docs = ['sale_deed', 'title_deed', 'encumbrance_certificate']
        features['missing_critical_docs'] = sum(
            1.0 for doc in critical_docs 
            if not any(doc.replace('_', ' ') in str(d).lower() for d in documents)
        )
        
        # Document completeness score
        features['document_completeness'] = min(len(documents) / 5.0, 1.0)
        
        return features
    
    def _temporal_features(self, record: Dict) -> Dict[str, float]:
        """Extract time-based features"""
        features = {}
        
        reg_date_str = record.get('registration_date', '')
        
        try:
            reg_date = datetime.strptime(reg_date_str, '%Y-%m-%d')
            now = datetime.now()
            
            # Days since registration
            days_since_reg = (now - reg_date).days
            features['days_since_registration'] = days_since_reg
            features['years_since_registration'] = days_since_reg / 365.25
            
            # Recent transaction flag
            features['is_recent_transaction'] = 1.0 if days_since_reg < 180 else 0.0
            
            # Registration year
            features['registration_year'] = reg_date.year
            
            # Month of registration (some months have more fraud)
            features['registration_month'] = reg_date.month
            
            # Weekend registration (suspicious)
            features['registered_on_weekend'] = 1.0 if reg_date.weekday() >= 5 else 0.0
            
        except:
            # Default values if date parsing fails
            features['days_since_registration'] = -1
            features['years_since_registration'] = -1
            features['is_recent_transaction'] = 0.0
            features['registration_year'] = 2000
            features['registration_month'] = 1
            features['registered_on_weekend'] = 0.0
        
        return features
    
    def _owner_features(self, record: Dict) -> Dict[str, float]:
        """Extract owner-related features"""
        features = {}
        
        owner_name = record.get('owner_name', '')
        seller_name = record.get('seller_name', '')
        
        # Name length (unusually short/long names are suspicious)
        features['owner_name_length'] = len(owner_name)
        features['owner_name_too_short'] = 1.0 if len(owner_name) < 3 else 0.0
        
        # Multiple owners
        owners = record.get('owners', [owner_name]) if owner_name else []
        features['num_owners'] = len(owners)
        features['is_multiple_owners'] = 1.0 if len(owners) > 1 else 0.0
        
        # Seller-buyer relationship (same name is suspicious)
        if seller_name:
            features['seller_buyer_same'] = 1.0 if owner_name.lower() == seller_name.lower() else 0.0
        else:
            features['seller_buyer_same'] = 0.0
        
        # Name pattern analysis
        features['has_numbers_in_name'] = 1.0 if re.search(r'\d', owner_name) else 0.0
        features['has_special_chars'] = 1.0 if re.search(r'[^a-zA-Z\s]', owner_name) else 0.0
        
        return features
    
    def _survey_features(self, record: Dict) -> Dict[str, float]:
        """Extract survey/area-related features"""
        features = {}
        
        survey_number = record.get('survey_number', '')
        area = record.get('area', 0) or 0
        
        # Survey number validity
        features['has_survey_number'] = 1.0 if survey_number else 0.0
        features['survey_number_length'] = len(str(survey_number))
        
        # Area features
        features['area_sqm'] = area
        features['area_magnitude'] = np.log10(area + 1)
        
        # Area size categories
        features['is_small_plot'] = 1.0 if 0 < area < 100 else 0.0
        features['is_medium_plot'] = 1.0 if 100 <= area < 1000 else 0.0
        features['is_large_plot'] = 1.0 if area >= 1000 else 0.0
        
        # Unusual area values
        features['area_is_round_number'] = 1.0 if area > 0 and area % 100 == 0 else 0.0
        
        return features
    
    def _transaction_features(self, record: Dict) -> Dict[str, float]:
        """Extract transaction-related features"""
        features = {}
        
        transaction_type = record.get('transaction_type', 'sale').lower()
        
        # Transaction type encoding
        features['is_sale'] = 1.0 if 'sale' in transaction_type else 0.0
        features['is_gift'] = 1.0 if 'gift' in transaction_type else 0.0
        features['is_inheritance'] = 1.0 if 'inherit' in transaction_type else 0.0
        features['is_lease'] = 1.0 if 'lease' in transaction_type else 0.0
        
        # Stamp duty and registration fees
        stamp_duty = record.get('stamp_duty', 0) or 0
        reg_fee = record.get('registration_fee', 0) or 0
        
        features['stamp_duty_paid'] = stamp_duty
        features['registration_fee_paid'] = reg_fee
        features['total_fees_paid'] = stamp_duty + reg_fee
        
        # Fee adequacy check
        price = record.get('price', 0) or 0
        if price > 0:
            expected_stamp_duty = price * 0.05  # Assuming 5% stamp duty
            features['stamp_duty_ratio'] = stamp_duty / expected_stamp_duty if expected_stamp_duty > 0 else 0
            features['underpaid_stamp_duty'] = 1.0 if stamp_duty < expected_stamp_duty * 0.8 else 0.0
        else:
            features['stamp_duty_ratio'] = 0.0
            features['underpaid_stamp_duty'] = 0.0
        
        return features
    
    def get_feature_vector(self, record: Dict) -> np.ndarray:
        """Get feature vector as numpy array"""
        features = self.extract_features(record)
        return np.array([features[name] for name in self.feature_names])
    
    def get_feature_names(self) -> List[str]:
        """Get list of all feature names"""
        return self.feature_names


# Example usage
if __name__ == "__main__":
    # Sample land record
    sample_record = {
        'owner_name': 'John Doe',
        'seller_name': 'Jane Smith',
        'survey_number': 'SY-123/45',
        'area': 500,  # square meters
        'price': 5000000,  # 50 lakhs
        'market_value': 5500000,
        'registration_date': '2024-06-15',
        'transaction_type': 'sale',
        'documents': ['sale_deed', 'title_deed', 'tax_receipt'],
        'stamp_duty': 250000,
        'registration_fee': 50000
    }
    
    engineer = FeatureEngineer()
    features = engineer.extract_features(sample_record)
    
    print("🔍 Extracted Features:")
    print("=" * 60)
    for name, value in features.items():
        print(f"{name:35s}: {value:.4f}")
    
    print(f"\n✅ Total features extracted: {len(features)}")