"""
LandGuard ML Pipeline
Integrated machine learning fraud detection pipeline
"""

import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

from feature_engineering import FeatureEngineer
from anomaly_detector import AnomalyDetector
from fraud_classifier import FraudClassifier, EnsembleFraudDetector
from pattern_learner import FraudPatternLearner, RiskScorer


class MLFraudDetectionPipeline:
    """
    Complete ML pipeline for fraud detection
    Combines feature engineering, anomaly detection, classification, and pattern matching
    """
    
    def __init__(self, models_dir: str = 'ml/models'):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.feature_engineer = FeatureEngineer()
        self.anomaly_detector = None
        self.classifier = None
        self.pattern_learner = None
        self.risk_scorer = None
        
        # Pipeline state
        self.is_trained = False
        self.training_stats = {}
    
    def train(self, 
             training_records: List[Dict],
             labels: Optional[List[int]] = None,
             fraud_cases: Optional[List[Dict]] = None):
        """
        Train the complete ML pipeline
        
        Args:
            training_records: All training records (fraud + normal)
            labels: Labels for supervised learning (0=normal, 1=fraud)
                   If None, only unsupervised methods will be trained
            fraud_cases: Confirmed fraud cases for pattern learning
        """
        print("=" * 70)
        print("🚀 LandGuard ML Pipeline Training")
        print("=" * 70)
        
        # Step 1: Feature Engineering
        print("\n1️⃣ Feature Engineering")
        print("-" * 70)
        features_list = []
        for record in training_records:
            features = self.feature_engineer.extract_features(record)
            features_list.append(list(features.values()))
        
        X = np.array(features_list)
        feature_names = self.feature_engineer.get_feature_names()
        
        print(f"✅ Extracted {X.shape[1]} features from {X.shape[0]} records")
        
        # Step 2: Train Anomaly Detector (Unsupervised)
        print("\n2️⃣ Anomaly Detection Training")
        print("-" * 70)
        self.anomaly_detector = AnomalyDetector(contamination=0.1)
        self.anomaly_detector.fit(X, feature_names)
        self.anomaly_detector.save(str(self.models_dir / 'anomaly_detector.pkl'))
        
        # Step 3: Train Classifier (Supervised - if labels provided)
        if labels is not None:
            print("\n3️⃣ Supervised Classification Training")
            print("-" * 70)
            y = np.array(labels)
            
            self.classifier = FraudClassifier(model_type='random_forest')
            metrics = self.classifier.train(X, y, feature_names)
            self.classifier.save(str(self.models_dir / 'fraud_classifier.pkl'))
            
            self.training_stats['classifier_metrics'] = metrics
        else:
            print("\n3️⃣ Supervised Classification - SKIPPED (no labels)")
        
        # Step 4: Learn Fraud Patterns
        if fraud_cases:
            print("\n4️⃣ Fraud Pattern Learning")
            print("-" * 70)
            self.pattern_learner = FraudPatternLearner()
            self.pattern_learner.learn_patterns(fraud_cases)
            self.pattern_learner.save(str(self.models_dir / 'fraud_patterns.json'))
        else:
            print("\n4️⃣ Fraud Pattern Learning - SKIPPED (no fraud cases)")
        
        # Step 5: Initialize Risk Scorer
        print("\n5️⃣ Risk Scorer Initialization")
        print("-" * 70)
        self.risk_scorer = RiskScorer(self.pattern_learner)
        print("✅ Risk scorer initialized")
        
        self.is_trained = True
        
        print("\n" + "=" * 70)
        print("✅ ML Pipeline Training Complete!")
        print("=" * 70)
        
        return self.training_stats
    
    def predict(self, record: Dict, 
               include_explanations: bool = True) -> Dict[str, Any]:
        """
        Run complete fraud detection on a single record
        
        Args:
            record: Land record to analyze
            include_explanations: Include detailed explanations
        
        Returns:
            Comprehensive fraud detection result
        """
        if not self.is_trained:
            raise ValueError("Pipeline not trained! Call train() first.")
        
        # Extract features
        features_dict = self.feature_engineer.extract_features(record)
        features = np.array(list(features_dict.values()))
        
        result = {
            'record_id': record.get('id', 'unknown'),
            'timestamp': str(np.datetime64('now')),
            'ml_predictions': {}
        }
        
        # 1. Anomaly Detection
        if self.anomaly_detector:
            is_anomaly, anomaly_score, anomaly_details = self.anomaly_detector.predict(features)
            result['ml_predictions']['anomaly_detection'] = {
                'is_anomaly': is_anomaly,
                'anomaly_score': float(anomaly_score),
                'details': anomaly_details
            }
            
            if include_explanations and is_anomaly:
                reasons = self.anomaly_detector.get_anomaly_reasons(
                    features, 
                    self.feature_engineer.get_feature_names()
                )
                result['ml_predictions']['anomaly_detection']['reasons'] = reasons
        
        # 2. Classification
        classifier_prob = None
        if self.classifier:
            is_fraud, fraud_prob, class_details = self.classifier.predict(features)
            classifier_prob = fraud_prob
            
            result['ml_predictions']['classification'] = {
                'is_fraud': is_fraud,
                'fraud_probability': float(fraud_prob),
                'details': class_details
            }
            
            if include_explanations:
                explanations = self.classifier.explain_prediction(features, top_n=5)
                result['ml_predictions']['classification']['top_features'] = [
                    {'feature': name, 'importance': float(imp), 'value': float(val)}
                    for name, imp, val in explanations
                ]
        
        # 3. Pattern Matching
        pattern_matches = []
        if self.pattern_learner:
            matches = self.pattern_learner.match_patterns(record, features_dict)
            pattern_matches = matches
            
            result['ml_predictions']['pattern_matching'] = {
                'matched_signatures': len(matches),
                'matches': matches
            }
        
        # 4. Comprehensive Risk Score
        if self.risk_scorer:
            risk_result = self.risk_scorer.calculate_risk_score(
                anomaly_score=anomaly_score if self.anomaly_detector else None,
                classifier_prob=classifier_prob,
                pattern_matches=pattern_matches,
                rule_violations=record.get('rule_violations', [])
            )
            
            result['risk_assessment'] = risk_result
        
        # 5. Final Verdict
        result['final_verdict'] = self._determine_verdict(result)
        
        return result
    
    def _determine_verdict(self, result: Dict) -> Dict[str, Any]:
        """Determine final fraud verdict based on all ML predictions"""
        risk_score = result.get('risk_assessment', {}).get('risk_score', 0)
        
        # Voting system
        votes = {'fraud': 0, 'normal': 0}
        confidence_scores = []
        
        # Anomaly detector vote
        if 'anomaly_detection' in result['ml_predictions']:
            if result['ml_predictions']['anomaly_detection']['is_anomaly']:
                votes['fraud'] += 1
                confidence_scores.append(
                    result['ml_predictions']['anomaly_detection']['anomaly_score']
                )
            else:
                votes['normal'] += 1
        
        # Classifier vote
        if 'classification' in result['ml_predictions']:
            if result['ml_predictions']['classification']['is_fraud']:
                votes['fraud'] += 1
                confidence_scores.append(
                    result['ml_predictions']['classification']['fraud_probability']
                )
            else:
                votes['normal'] += 1
        
        # Pattern matching vote
        if 'pattern_matching' in result['ml_predictions']:
            if result['ml_predictions']['pattern_matching']['matched_signatures'] > 0:
                votes['fraud'] += 1
        
        # Determine verdict
        is_fraud = votes['fraud'] > votes['normal'] or risk_score >= 50
        
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.5
        
        return {
            'is_fraudulent': is_fraud,
            'confidence': float(avg_confidence),
            'votes': votes,
            'risk_score': risk_score,
            'recommendation': self._get_recommendation(risk_score, is_fraud)
        }
    
    def _get_recommendation(self, risk_score: float, is_fraud: bool) -> str:
        """Get action recommendation based on risk"""
        if risk_score >= 75:
            return "REJECT - Critical fraud indicators detected"
        elif risk_score >= 50:
            return "INVESTIGATE - High fraud risk, thorough verification required"
        elif risk_score >= 25:
            return "REVIEW - Moderate risk, additional documentation needed"
        else:
            return "APPROVE - Low fraud risk, standard processing"
    
    def batch_predict(self, records: List[Dict]) -> List[Dict]:
        """Run fraud detection on multiple records"""
        results = []
        
        print(f"🔍 Analyzing {len(records)} records...")
        
        for i, record in enumerate(records):
            if i % 10 == 0:
                print(f"   Progress: {i}/{len(records)}")
            
            result = self.predict(record, include_explanations=False)
            results.append(result)
        
        print(f"✅ Analysis complete!")
        
        return results
    
    def load_models(self):
        """Load pre-trained models from disk"""
        print("📂 Loading pre-trained models...")
        
        # Load anomaly detector
        anomaly_path = self.models_dir / 'anomaly_detector.pkl'
        if anomaly_path.exists():
            self.anomaly_detector = AnomalyDetector.load(str(anomaly_path))
        
        # Load classifier
        classifier_path = self.models_dir / 'fraud_classifier.pkl'
        if classifier_path.exists():
            self.classifier = FraudClassifier.load(str(classifier_path))
        
        # Load patterns
        patterns_path = self.models_dir / 'fraud_patterns.json'
        if patterns_path.exists():
            self.pattern_learner = FraudPatternLearner.load(str(patterns_path))
        
        # Initialize risk scorer
        self.risk_scorer = RiskScorer(self.pattern_learner)
        
        # Initialize feature engineer
        self.feature_engineer = FeatureEngineer()
        
        self.is_trained = True
        print("✅ Models loaded successfully!")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        info = {
            'is_trained': self.is_trained,
            'models_dir': str(self.models_dir),
            'components': {}
        }
        
        if self.anomaly_detector:
            info['components']['anomaly_detector'] = self.anomaly_detector.get_statistics()
        
        if self.classifier:
            info['components']['classifier'] = {
                'model_type': self.classifier.model_type,
                'is_trained': self.classifier.is_trained,
                'top_features': self.classifier.get_top_features(5)
            }
        
        if self.pattern_learner:
            info['components']['pattern_learner'] = {
                'num_signatures': len(self.pattern_learner.fraud_signatures),
                'is_trained': self.pattern_learner.is_trained
            }
        
        return info


# Example usage
if __name__ == "__main__":
    print("🚀 LandGuard ML Pipeline Demo\n")
    
    # Create sample training data
    training_data = []
    labels = []
    
    # Normal records
    for i in range(100):
        record = {
            'id': f'normal_{i}',
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
        training_data.append(record)
        labels.append(0)
    
    # Fraud records
    fraud_cases = []
    for i in range(30):
        record = {
            'id': f'fraud_{i}',
            'owner_name': f'X{i}',
            'seller_name': f'X{i}',
            'survey_number': '',
            'area': np.random.randint(20, 100),
            'price': np.random.randint(50000, 500000),
            'market_value': np.random.randint(3000000, 8000000),
            'registration_date': '2024-12-25',
            'transaction_type': 'gift',
            'documents': ['sale_deed'],
            'stamp_duty': 5000,
            'registration_fee': 1000
        }
        training_data.append(record)
        labels.append(1)
        fraud_cases.append(record)
    
    # Initialize and train pipeline
    pipeline = MLFraudDetectionPipeline()
    stats = pipeline.train(training_data, labels, fraud_cases)
    
    # Test on a suspicious record
    print("\n" + "=" * 70)
    print("🔍 Testing on Suspicious Record")
    print("=" * 70)
    
    test_record = {
        'id': 'test_001',
        'owner_name': 'ABC',
        'seller_name': 'ABC',
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
    
    result = pipeline.predict(test_record)
    
    # Display results
    print(f"\n📋 Analysis Results for: {result['record_id']}")
    print("-" * 70)
    
    verdict = result['final_verdict']
    risk = result['risk_assessment']
    
    print(f"\n{risk['risk_color']} RISK SCORE: {risk['risk_score']}/100")
    print(f"   Risk Level: {risk['risk_level']}")
    print(f"   {risk['interpretation']}")
    
    print(f"\n{'🚨 FRAUD DETECTED' if verdict['is_fraudulent'] else '✅ NORMAL RECORD'}")
    print(f"   Confidence: {verdict['confidence']:.2%}")
    print(f"   Recommendation: {verdict['recommendation']}")
    
    print(f"\n📊 Component Breakdown:")
    for component, score in risk['component_scores'].items():
        print(f"   {component:20s}: {score:.2f}/100")
    
    # Save result to JSON
    output_path = 'ml/results/test_prediction.json'
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n💾 Full results saved to: {output_path}")