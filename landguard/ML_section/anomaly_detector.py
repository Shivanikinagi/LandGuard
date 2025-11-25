"""
LandGuard Anomaly Detection
Unsupervised fraud detection using Isolation Forest and statistical methods
"""

import numpy as np
import pickle
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from typing import Dict, List, Tuple, Any
from pathlib import Path


class AnomalyDetector:
    """Detect anomalous land records using unsupervised learning"""
    
    def __init__(self, contamination: float = 0.1):
        """
        Initialize anomaly detector
        
        Args:
            contamination: Expected proportion of anomalies (0.0 to 0.5)
                          0.1 = expect 10% of records to be fraudulent
        """
        self.contamination = contamination
        
        # Isolation Forest - best for anomaly detection
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        
        # DBSCAN for density-based clustering
        self.dbscan = DBSCAN(eps=0.5, min_samples=5)
        
        # Feature scaler
        self.scaler = StandardScaler()
        
        # Trained flag
        self.is_trained = False
        
        # Feature importance (calculated during training)
        self.feature_importance = {}
    
    def fit(self, features: np.ndarray, feature_names: List[str] = None):
        """
        Train anomaly detector on historical data
        
        Args:
            features: 2D array of shape (n_samples, n_features)
            feature_names: List of feature names for interpretation
        """
        print(f"🎓 Training anomaly detector on {len(features)} records...")
        
        # Scale features
        self.scaler.fit(features)
        features_scaled = self.scaler.transform(features)
        
        # Train Isolation Forest
        self.isolation_forest.fit(features_scaled)
        
        # Train DBSCAN
        self.dbscan.fit(features_scaled)
        
        # Calculate feature importance using decision path depth
        if feature_names:
            self._calculate_feature_importance(features_scaled, feature_names)
        
        self.is_trained = True
        print("✅ Anomaly detector trained successfully!")
    
    def predict(self, features: np.ndarray) -> Tuple[bool, float, Dict]:
        """
        Predict if a record is anomalous
        
        Args:
            features: 1D array of features for a single record
        
        Returns:
            Tuple of (is_anomaly, anomaly_score, details)
        """
        if not self.is_trained:
            raise ValueError("Detector not trained! Call fit() first.")
        
        # Reshape if needed
        if features.ndim == 1:
            features = features.reshape(1, -1)
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Get Isolation Forest prediction
        if_prediction = self.isolation_forest.predict(features_scaled)[0]
        if_score = self.isolation_forest.score_samples(features_scaled)[0]
        
        # Get DBSCAN cluster
        dbscan_label = self.dbscan.fit_predict(features_scaled)[0]
        
        # Convert to probability-like score (0 to 1)
        # Isolation Forest score is negative (more negative = more anomalous)
        anomaly_score = self._normalize_score(if_score)
        
        # Determine if anomalous
        is_anomaly = (if_prediction == -1) or (dbscan_label == -1)
        
        # Detailed analysis
        details = {
            'isolation_forest_score': float(if_score),
            'normalized_score': float(anomaly_score),
            'dbscan_cluster': int(dbscan_label),
            'is_outlier': bool(dbscan_label == -1),
            'confidence': float(abs(if_score)),
            'method': 'isolation_forest+dbscan'
        }
        
        return is_anomaly, anomaly_score, details
    
    def batch_predict(self, features_batch: np.ndarray) -> List[Tuple[bool, float, Dict]]:
        """
        Predict anomalies for multiple records
        
        Args:
            features_batch: 2D array of shape (n_samples, n_features)
        
        Returns:
            List of (is_anomaly, score, details) for each record
        """
        results = []
        
        for features in features_batch:
            result = self.predict(features)
            results.append(result)
        
        return results
    
    def get_anomaly_reasons(self, features: np.ndarray, 
                           feature_names: List[str]) -> List[str]:
        """
        Explain why a record was flagged as anomalous
        
        Args:
            features: Feature vector of the anomalous record
            feature_names: Names of features
        
        Returns:
            List of reasons (feature-based explanations)
        """
        if not self.is_trained:
            return ["Detector not trained"]
        
        reasons = []
        features_scaled = self.scaler.transform(features.reshape(1, -1))[0]
        
        # Find features with extreme values
        for i, (name, value, scaled_value) in enumerate(
            zip(feature_names, features, features_scaled)
        ):
            # Check if feature is an outlier (> 2 std from mean)
            if abs(scaled_value) > 2.0:
                direction = "high" if scaled_value > 0 else "low"
                reasons.append(
                    f"{name} is unusually {direction} ({value:.2f}, z-score: {scaled_value:.2f})"
                )
        
        # Add top contributing features based on importance
        if self.feature_importance:
            top_features = sorted(
                self.feature_importance.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3]
            
            reasons.append(f"Top anomaly indicators: {', '.join([f[0] for f in top_features])}")
        
        return reasons[:5]  # Return top 5 reasons
    
    def _normalize_score(self, if_score: float) -> float:
        """Convert Isolation Forest score to 0-1 range"""
        # Isolation Forest scores typically range from -0.5 to 0.5
        # More negative = more anomalous
        # Normalize to 0 (normal) to 1 (highly anomalous)
        normalized = (0.5 - if_score) / 1.0  # Invert and scale
        return np.clip(normalized, 0, 1)
    
    def _calculate_feature_importance(self, features: np.ndarray, 
                                      feature_names: List[str]):
        """Calculate which features contribute most to anomaly detection"""
        # Use variance as a proxy for importance
        variances = np.var(features, axis=0)
        
        for name, variance in zip(feature_names, variances):
            self.feature_importance[name] = float(variance)
    
    def save(self, model_path: str):
        """Save trained model to disk"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'isolation_forest': self.isolation_forest,
            'dbscan': self.dbscan,
            'scaler': self.scaler,
            'contamination': self.contamination,
            'feature_importance': self.feature_importance,
            'is_trained': self.is_trained
        }
        
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"💾 Model saved to {model_path}")
    
    @classmethod
    def load(cls, model_path: str):
        """Load trained model from disk"""
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        detector = cls(contamination=model_data['contamination'])
        detector.isolation_forest = model_data['isolation_forest']
        detector.dbscan = model_data['dbscan']
        detector.scaler = model_data['scaler']
        detector.feature_importance = model_data['feature_importance']
        detector.is_trained = model_data['is_trained']
        
        print(f"📂 Model loaded from {model_path}")
        return detector
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the trained detector"""
        if not self.is_trained:
            return {"status": "not_trained"}
        
        return {
            "status": "trained",
            "contamination_rate": self.contamination,
            "n_estimators": self.isolation_forest.n_estimators,
            "feature_importance": dict(sorted(
                self.feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),  # Top 10 important features
            "scaler_mean": self.scaler.mean_.tolist() if hasattr(self.scaler, 'mean_') else None,
            "scaler_std": self.scaler.scale_.tolist() if hasattr(self.scaler, 'scale_') else None
        }


# Statistical Anomaly Detection (for comparison)
class StatisticalAnomalyDetector:
    """Simple statistical anomaly detection using Z-scores"""
    
    def __init__(self, threshold: float = 3.0):
        """
        Args:
            threshold: Z-score threshold (typically 2.5-3.0)
        """
        self.threshold = threshold
        self.means = None
        self.stds = None
    
    def fit(self, features: np.ndarray):
        """Calculate mean and std for each feature"""
        self.means = np.mean(features, axis=0)
        self.stds = np.std(features, axis=0)
    
    def predict(self, features: np.ndarray) -> Tuple[bool, float, List[int]]:
        """
        Predict using Z-score method
        
        Returns:
            (is_anomaly, max_z_score, anomalous_feature_indices)
        """
        if self.means is None:
            raise ValueError("Detector not fitted")
        
        # Calculate Z-scores
        z_scores = np.abs((features - self.means) / (self.stds + 1e-10))
        
        # Find anomalous features
        anomalous_features = np.where(z_scores > self.threshold)[0]
        
        is_anomaly = len(anomalous_features) > 0
        max_z_score = float(np.max(z_scores))
        
        return is_anomaly, max_z_score, anomalous_features.tolist()


# Example usage
if __name__ == "__main__":
    from feature_engineering import FeatureEngineer
    
    # Generate sample training data
    print("🔧 Generating sample training data...")
    
    engineer = FeatureEngineer()
    
    # Normal records
    normal_records = []
    for i in range(90):
        record = {
            'owner_name': f'Owner {i}',
            'seller_name': f'Seller {i}',
            'survey_number': f'SY-{i}',
            'area': np.random.randint(200, 1000),
            'price': np.random.randint(2000000, 8000000),
            'market_value': np.random.randint(2000000, 8000000),
            'registration_date': '2024-06-15',
            'transaction_type': 'sale',
            'documents': ['sale_deed', 'title_deed', 'tax_receipt'],
            'stamp_duty': 250000,
            'registration_fee': 50000
        }
        features = engineer.extract_features(record)
        normal_records.append(list(features.values()))
    
    # Fraudulent records (anomalies)
    fraud_records = []
    for i in range(10):
        record = {
            'owner_name': f'X{i}',  # Suspicious name
            'seller_name': f'X{i}',  # Same as owner!
            'survey_number': '',  # Missing
            'area': 50,  # Unusually small
            'price': 100000,  # Too low
            'market_value': 5000000,  # Huge deviation
            'registration_date': '2024-12-25',  # Holiday
            'transaction_type': 'gift',
            'documents': ['sale_deed'],  # Missing docs
            'stamp_duty': 5000,  # Underpaid
            'registration_fee': 1000
        }
        features = engineer.extract_features(record)
        fraud_records.append(list(features.values()))
    
    # Combine and convert to numpy
    all_features = np.array(normal_records + fraud_records)
    
    print(f"✅ Created {len(all_features)} sample records (90 normal, 10 fraud)")
    
    # Train detector
    detector = AnomalyDetector(contamination=0.1)
    detector.fit(all_features, engineer.get_feature_names())
    
    # Test on a suspicious record
    print("\n🔍 Testing on suspicious record...")
    test_record = {
        'owner_name': 'ABC',
        'seller_name': 'ABC',  # Same!
        'survey_number': '',
        'area': 30,
        'price': 50000,
        'market_value': 6000000,
        'registration_date': '2024-06-15',
        'transaction_type': 'gift',
        'documents': [],
        'stamp_duty': 1000,
        'registration_fee': 500
    }
    
    test_features = engineer.get_feature_vector(test_record)
    is_anomaly, score, details = detector.predict(test_features)
    
    print(f"\n{'🚨 ANOMALY DETECTED' if is_anomaly else '✅ Normal Record'}")
    print(f"Anomaly Score: {score:.4f}")
    print(f"Details: {details}")
    
    # Get reasons
    reasons = detector.get_anomaly_reasons(
        test_features, 
        engineer.get_feature_names()
    )
    print("\n📋 Anomaly Reasons:")
    for reason in reasons:
        print(f"  • {reason}")
    
    # Save model
    detector.save('ml/models/anomaly_detector.pkl')