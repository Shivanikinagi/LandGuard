"""
LandGuard Fraud Classifier
Supervised learning model for fraud classification
"""

import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from typing import Dict, List, Tuple, Any
from pathlib import Path


class FraudClassifier:
    """Supervised fraud classification using ensemble methods"""
    
    def __init__(self, model_type: str = 'random_forest'):
        """
        Initialize fraud classifier
        
        Args:
            model_type: 'random_forest' or 'gradient_boosting'
        """
        self.model_type = model_type
        
        # Initialize model
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                class_weight='balanced',  # Handle imbalanced data
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Feature scaler
        self.scaler = StandardScaler()
        
        # Training metrics
        self.is_trained = False
        self.feature_names = []
        self.feature_importance = {}
        self.training_metrics = {}
    
    def train(self, features: np.ndarray, labels: np.ndarray, 
              feature_names: List[str] = None, 
              validation_split: float = 0.2) -> Dict[str, Any]:
        """
        Train the fraud classifier
        
        Args:
            features: 2D array of shape (n_samples, n_features)
            labels: 1D array of shape (n_samples,) with 0=normal, 1=fraud
            feature_names: List of feature names
            validation_split: Fraction of data to use for validation
        
        Returns:
            Dictionary with training metrics
        """
        print(f"🎓 Training {self.model_type} classifier...")
        print(f"   Total samples: {len(labels)}")
        print(f"   Fraud cases: {np.sum(labels)} ({np.mean(labels)*100:.1f}%)")
        
        # Store feature names
        if feature_names:
            self.feature_names = feature_names
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            features, labels, 
            test_size=validation_split, 
            random_state=42,
            stratify=labels  # Maintain class distribution
        )
        
        print(f"   Training set: {len(X_train)} samples")
        print(f"   Validation set: {len(X_val)} samples")
        
        # Scale features
        self.scaler.fit(X_train)
        X_train_scaled = self.scaler.transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Train model
        print("\n⚙️  Training model...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate on validation set
        val_predictions = self.model.predict(X_val_scaled)
        val_probabilities = self.model.predict_proba(X_val_scaled)[:, 1]
        
        # Calculate metrics
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        self.training_metrics = {
            'accuracy': float(accuracy_score(y_val, val_predictions)),
            'precision': float(precision_score(y_val, val_predictions, zero_division=0)),
            'recall': float(recall_score(y_val, val_predictions, zero_division=0)),
            'f1_score': float(f1_score(y_val, val_predictions, zero_division=0)),
            'roc_auc': float(roc_auc_score(y_val, val_probabilities)) if len(np.unique(y_val)) > 1 else 0.0,
            'confusion_matrix': confusion_matrix(y_val, val_predictions).tolist()
        }
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            if feature_names:
                self.feature_importance = {
                    name: float(importance) 
                    for name, importance in zip(feature_names, importances)
                }
        
        self.is_trained = True
        
        # Print results
        print("\n✅ Training complete!")
        print(f"   Accuracy:  {self.training_metrics['accuracy']:.4f}")
        print(f"   Precision: {self.training_metrics['precision']:.4f}")
        print(f"   Recall:    {self.training_metrics['recall']:.4f}")
        print(f"   F1 Score:  {self.training_metrics['f1_score']:.4f}")
        print(f"   ROC-AUC:   {self.training_metrics['roc_auc']:.4f}")
        
        return self.training_metrics
    
    def predict(self, features: np.ndarray) -> Tuple[bool, float, Dict]:
        """
        Predict if a record is fraudulent
        
        Args:
            features: 1D or 2D array of features
        
        Returns:
            Tuple of (is_fraud, fraud_probability, details)
        """
        if not self.is_trained:
            raise ValueError("Classifier not trained! Call train() first.")
        
        # Reshape if needed
        if features.ndim == 1:
            features = features.reshape(1, -1)
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        probability = self.model.predict_proba(features_scaled)[0]
        
        is_fraud = bool(prediction == 1)
        fraud_prob = float(probability[1])
        
        details = {
            'prediction': int(prediction),
            'fraud_probability': fraud_prob,
            'normal_probability': float(probability[0]),
            'confidence': max(probability),
            'model_type': self.model_type
        }
        
        return is_fraud, fraud_prob, details
    
    def batch_predict(self, features_batch: np.ndarray) -> List[Tuple[bool, float, Dict]]:
        """Predict for multiple records"""
        results = []
        
        # Scale all features at once
        features_scaled = self.scaler.transform(features_batch)
        
        # Predict
        predictions = self.model.predict(features_scaled)
        probabilities = self.model.predict_proba(features_scaled)
        
        for pred, prob in zip(predictions, probabilities):
            is_fraud = bool(pred == 1)
            fraud_prob = float(prob[1])
            
            details = {
                'prediction': int(pred),
                'fraud_probability': fraud_prob,
                'normal_probability': float(prob[0]),
                'confidence': max(prob),
                'model_type': self.model_type
            }
            
            results.append((is_fraud, fraud_prob, details))
        
        return results
    
    def explain_prediction(self, features: np.ndarray, 
                          top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Explain which features contributed most to the prediction
        
        Args:
            features: Feature vector
            top_n: Number of top contributing features to return
        
        Returns:
            List of (feature_name, contribution_score) tuples
        """
        if not self.is_trained or not self.feature_importance:
            return []
        
        # Get feature importances
        sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        # Combine with actual feature values
        explanations = []
        for name, importance in sorted_features:
            if name in self.feature_names:
                idx = self.feature_names.index(name)
                value = features[idx] if features.ndim == 1 else features[0][idx]
                explanations.append((name, float(importance), float(value)))
        
        return explanations
    
    def get_top_features(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """Get most important features for fraud detection"""
        if not self.feature_importance:
            return []
        
        return sorted(
            self.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
    
    def save(self, model_path: str):
        """Save trained classifier"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance,
            'training_metrics': self.training_metrics,
            'is_trained': self.is_trained
        }
        
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"💾 Classifier saved to {model_path}")
    
    @classmethod
    def load(cls, model_path: str):
        """Load trained classifier"""
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        classifier = cls(model_type=model_data['model_type'])
        classifier.model = model_data['model']
        classifier.scaler = model_data['scaler']
        classifier.feature_names = model_data['feature_names']
        classifier.feature_importance = model_data['feature_importance']
        classifier.training_metrics = model_data['training_metrics']
        classifier.is_trained = model_data['is_trained']
        
        print(f"📂 Classifier loaded from {model_path}")
        return classifier
    
    def cross_validate(self, features: np.ndarray, labels: np.ndarray, 
                      cv: int = 5) -> Dict[str, float]:
        """Perform cross-validation"""
        print(f"🔄 Performing {cv}-fold cross-validation...")
        
        features_scaled = self.scaler.fit_transform(features)
        
        scores = cross_val_score(
            self.model, features_scaled, labels,
            cv=cv, scoring='f1'
        )
        
        cv_results = {
            'mean_f1': float(np.mean(scores)),
            'std_f1': float(np.std(scores)),
            'scores': scores.tolist()
        }
        
        print(f"   Mean F1: {cv_results['mean_f1']:.4f} (+/- {cv_results['std_f1']:.4f})")
        
        return cv_results


# Ensemble Fraud Detector (combines multiple models)
class EnsembleFraudDetector:
    """Combines multiple classifiers for robust predictions"""
    
    def __init__(self):
        self.classifiers = []
        self.weights = []
    
    def add_classifier(self, classifier: FraudClassifier, weight: float = 1.0):
        """Add a classifier to the ensemble"""
        self.classifiers.append(classifier)
        self.weights.append(weight)
    
    def predict(self, features: np.ndarray) -> Tuple[bool, float, Dict]:
        """Weighted voting prediction"""
        if not self.classifiers:
            raise ValueError("No classifiers in ensemble")
        
        predictions = []
        probabilities = []
        
        for clf in self.classifiers:
            _, prob, _ = clf.predict(features)
            probabilities.append(prob)
        
        # Weighted average
        weighted_prob = np.average(probabilities, weights=self.weights)
        is_fraud = weighted_prob > 0.5
        
        details = {
            'ensemble_probability': float(weighted_prob),
            'individual_probabilities': [float(p) for p in probabilities],
            'num_classifiers': len(self.classifiers),
            'weights': self.weights
        }
        
        return is_fraud, weighted_prob, details


# Example usage
if __name__ == "__main__":
    from feature_engineering import FeatureEngineer
    
    print("🔧 Generating labeled training data...")
    
    engineer = FeatureEngineer()
    
    # Generate features and labels
    all_features = []
    all_labels = []
    
    # Normal records (label=0)
    for i in range(150):
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
        all_features.append(list(features.values()))
        all_labels.append(0)  # Normal
    
    # Fraud records (label=1)
    for i in range(50):
        record = {
            'owner_name': f'X{i}',
            'seller_name': f'X{i}',
            'survey_number': '',
            'area': np.random.randint(20, 100),
            'price': np.random.randint(50000, 500000),
            'market_value': np.random.randint(3000000, 8000000),
            'registration_date': '2024-12-25',
            'transaction_type': np.random.choice(['gift', 'sale']),
            'documents': ['sale_deed'],
            'stamp_duty': 5000,
            'registration_fee': 1000
        }
        features = engineer.extract_features(record)
        all_features.append(list(features.values()))
        all_labels.append(1)  # Fraud
    
    X = np.array(all_features)
    y = np.array(all_labels)
    
    print(f"✅ Created {len(y)} labeled samples (150 normal, 50 fraud)\n")
    
    # Train classifier
    classifier = FraudClassifier(model_type='random_forest')
    metrics = classifier.train(X, y, engineer.get_feature_names())
    
    # Test prediction
    print("\n🔍 Testing prediction on suspicious record...")
    test_record = {
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
    
    test_features = engineer.get_feature_vector(test_record)
    is_fraud, prob, details = classifier.predict(test_features)
    
    print(f"\n{'🚨 FRAUD DETECTED' if is_fraud else '✅ Normal Record'}")
    print(f"Fraud Probability: {prob:.4f}")
    print(f"Details: {details}")
    
    # Get top contributing features
    print("\n📊 Top Contributing Features:")
    for name, importance, value in classifier.explain_prediction(test_features, top_n=5):
        print(f"  • {name}: {importance:.4f} (value: {value:.2f})")
    
    # Save model
    classifier.save('ml/models/fraud_classifier.pkl')