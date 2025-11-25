# 🤖 Phase 7: Machine Learning Enhancement - Complete Guide

## 📋 Overview

Phase 7 adds intelligent fraud detection capabilities to LandGuard using multiple machine learning techniques:

- **Unsupervised Anomaly Detection** - Identifies unusual patterns
- **Supervised Classification** - Predicts fraud probability
- **Pattern Learning** - Learns fraud signatures
- **Risk Scoring** - Comprehensive risk assessment
- **Explainable AI** - Provides reasons for predictions

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ML FRAUD DETECTION PIPELINE               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Feature Engineering (40+ features)                       │
│     ├─ Price features (deviation, magnitude)                 │
│     ├─ Document features (completeness, missing docs)        │
│     ├─ Temporal features (date patterns, seasonality)        │
│     ├─ Owner features (name analysis, relationships)         │
│     └─ Transaction features (type, fees, compliance)         │
│                           ↓                                   │
│  2. Anomaly Detection (Unsupervised)                         │
│     ├─ Isolation Forest (100 estimators)                     │
│     ├─ DBSCAN Clustering                                     │
│     └─ Statistical Z-score Analysis                          │
│                           ↓                                   │
│  3. Fraud Classification (Supervised)                        │
│     ├─ Random Forest Classifier (200 trees)                  │
│     ├─ Gradient Boosting (optional)                          │
│     └─ Feature Importance Ranking                            │
│                           ↓                                   │
│  4. Pattern Matching                                         │
│     ├─ Learn fraud signatures from history                   │
│     ├─ Match records against known patterns                  │
│     └─ 5 pre-defined fraud signatures                        │
│                           ↓                                   │
│  5. Risk Scoring                                             │
│     ├─ Weighted combination of all signals                   │
│     ├─ Risk categorization (Low/Medium/High/Critical)        │
│     └─ Actionable recommendations                            │
│                           ↓                                   │
│  📊 FINAL VERDICT + EXPLANATIONS                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites

```bash
# Python 3.8+
python --version

# Existing LandGuard installation
# (Core analyzer, extractors, CLI should be working)
```

### Install ML Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install ML libraries
pip install scikit-learn==1.3.0
pip install numpy==1.24.3
pip install scipy==1.11.1

# Optional: For visualization
pip install matplotlib seaborn plotly
```

### Verify Installation

```bash
python -c "import sklearn; print(f'scikit-learn {sklearn.__version__}')"
python -c "import numpy; print(f'numpy {numpy.__version__}')"
```

---

## 🚀 Quick Start

### 1. Project Structure

Create the ML module directory:

```bash
cd landguard
mkdir -p ml/models ml/data ml/results
```

Add the ML files:

```
landguard/
├── ml/
│   ├── __init__.py
│   ├── feature_engineering.py    # ← Artifact 1
│   ├── anomaly_detector.py       # ← Artifact 2
│   ├── fraud_classifier.py       # ← Artifact 3
│   ├── pattern_learner.py        # ← Artifact 4
│   └── ml_pipeline.py            # ← Artifact 5
├── ml/models/                    # Saved models
├── ml/data/                      # Training data
└── ml/results/                   # Prediction results
```

### 2. Prepare Training Data

Create a training dataset CSV:

```python
# scripts/prepare_training_data.py
import pandas as pd
import numpy as np

# Generate sample data (replace with real data)
data = []

# Normal records
for i in range(200):
    data.append({
        'id': f'normal_{i}',
        'owner_name': f'Owner {i}',
        'seller_name': f'Seller {i}',
        'survey_number': f'SY-{i}/2024',
        'area': np.random.randint(200, 1000),
        'price': np.random.randint(2000000, 8000000),
        'market_value': np.random.randint(2000000, 8000000),
        'registration_date': '2024-06-15',
        'transaction_type': 'sale',
        'documents': 'sale_deed,title_deed,tax_receipt',
        'stamp_duty': 250000,
        'registration_fee': 50000,
        'is_fraud': 0
    })

# Fraud records
for i in range(50):
    data.append({
        'id': f'fraud_{i}',
        'owner_name': f'X{i}',
        'seller_name': f'X{i}',
        'survey_number': '',
        'area': np.random.randint(20, 100),
        'price': np.random.randint(50000, 500000),
        'market_value': np.random.randint(3000000, 8000000),
        'registration_date': '2024-12-25',
        'transaction_type': 'gift',
        'documents': 'sale_deed',
        'stamp_duty': 5000,
        'registration_fee': 1000,
        'is_fraud': 1
    })

df = pd.DataFrame(data)
df.to_csv('ml/data/training_data.csv', index=False)
print(f"✅ Created {len(df)} training records")
```

### 3. Train Models

```python
# scripts/train_models.py
from ml.ml_pipeline import MLFraudDetectionPipeline
import pandas as pd
import json

# Load training data
df = pd.read_csv('ml/data/training_data.csv')

# Convert to list of dictionaries
records = df.to_dict('records')

# Parse documents field
for record in records:
    docs = record.get('documents', '')
    record['documents'] = docs.split(',') if docs else []

# Split into training records and labels
training_records = records
labels = [r['is_fraud'] for r in records]
fraud_cases = [r for r in records if r['is_fraud'] == 1]

# Initialize and train pipeline
pipeline = MLFraudDetectionPipeline(models_dir='ml/models')
stats = pipeline.train(
    training_records=training_records,
    labels=labels,
    fraud_cases=fraud_cases
)

print("\n✅ Training complete!")
print(f"📊 Statistics: {json.dumps(stats, indent=2)}")
```

Run training:

```bash
python scripts/train_models.py
```

Expected output:
```
======================================================================
🚀 LandGuard ML Pipeline Training
======================================================================

1️⃣ Feature Engineering
----------------------------------------------------------------------
✅ Extracted 45 features from 250 records

2️⃣ Anomaly Detection Training
----------------------------------------------------------------------
🎓 Training anomaly detector on 250 records...
✅ Anomaly detector trained successfully!
💾 Model saved to ml/models/anomaly_detector.pkl

3️⃣ Supervised Classification Training
----------------------------------------------------------------------
🎓 Training random_forest classifier...
   Total samples: 250
   Fraud cases: 50 (20.0%)
   Training set: 200 samples
   Validation set: 50 samples

⚙️  Training model...

✅ Training complete!
   Accuracy:  0.9600
   Precision: 0.9231
   Recall:    0.9000
   F1 Score:  0.9114
   ROC-AUC:   0.9800

💾 Classifier saved to ml/models/fraud_classifier.pkl

4️⃣ Fraud Pattern Learning
----------------------------------------------------------------------
🧠 Learning fraud patterns from 50 fraud cases...
   📊 Learned 12 price patterns
   📄 Learned 5 document patterns
   📅 Learned 3 temporal patterns
   👤 Learned 2 owner patterns
✅ Pattern learning complete!
   Learned 5 fraud signatures
💾 Patterns saved to ml/models/fraud_patterns.json

5️⃣ Risk Scorer Initialization
----------------------------------------------------------------------
✅ Risk scorer initialized

======================================================================
✅ ML Pipeline Training Complete!
======================================================================
```

### 4. Run Predictions

```python
# scripts/predict_fraud.py
from ml.ml_pipeline import MLFraudDetectionPipeline
import json

# Load trained pipeline
pipeline = MLFraudDetectionPipeline(models_dir='ml/models')
pipeline.load_models()

# Test record
test_record = {
    'id': 'TEST_001',
    'owner_name': 'Suspicious Person',
    'seller_name': 'Suspicious Person',  # Same name!
    'survey_number': '',  # Missing
    'area': 50,  # Small
    'price': 100000,  # Very low
    'market_value': 5000000,  # High market value
    'registration_date': '2024-12-25',  # Holiday
    'transaction_type': 'gift',
    'documents': [],  # No documents!
    'stamp_duty': 1000,  # Underpaid
    'registration_fee': 500
}

# Predict
result = pipeline.predict(test_record, include_explanations=True)

# Display results
verdict = result['final_verdict']
risk = result['risk_assessment']

print(f"\n{'='*70}")
print(f"🔍 FRAUD ANALYSIS REPORT")
print(f"{'='*70}")
print(f"\nRecord ID: {result['record_id']}")
print(f"Timestamp: {result['timestamp']}")

print(f"\n{risk['risk_color']} RISK SCORE: {risk['risk_score']}/100")
print(f"Risk Level: {risk['risk_level']}")
print(f"{risk['interpretation']}")

print(f"\n{'🚨 FRAUD DETECTED!' if verdict['is_fraudulent'] else '✅ Normal Record'}")
print(f"Confidence: {verdict['confidence']:.1%}")
print(f"Recommendation: {verdict['recommendation']}")

print(f"\n📊 ML PREDICTIONS:")
print(f"{'─'*70}")

# Anomaly Detection
if 'anomaly_detection' in result['ml_predictions']:
    ad = result['ml_predictions']['anomaly_detection']
    print(f"\n1. Anomaly Detection:")
    print(f"   Anomaly: {ad['is_anomaly']}")
    print(f"   Score: {ad['anomaly_score']:.4f}")
    if 'reasons' in ad:
        print(f"   Reasons:")
        for reason in ad['reasons']:
            print(f"      • {reason}")

# Classification
if 'classification' in result['ml_predictions']:
    clf = result['ml_predictions']['classification']
    print(f"\n2. Fraud Classification:")
    print(f"   Fraud: {clf['is_fraud']}")
    print(f"   Probability: {clf['fraud_probability']:.1%}")
    if 'top_features' in clf:
        print(f"   Top Contributing Features:")
        for feat in clf['top_features'][:3]:
            print(f"      • {feat['feature']}: {feat['importance']:.3f}")

# Pattern Matching
if 'pattern_matching' in result['ml_predictions']:
    pm = result['ml_predictions']['pattern_matching']
    print(f"\n3. Pattern Matching:")
    print(f"   Matched Signatures: {pm['matched_signatures']}")
    for match in pm['matches']:
        print(f"   • {match['signature']} ({match['severity']})")
        print(f"     Confidence: {match['confidence']:.1%}")

# Save to JSON
with open(f"ml/results/{test_record['id']}_result.json", 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n💾 Full report saved to ml/results/{test_record['id']}_result.json")
```

Run prediction:

```bash
python scripts/predict_fraud.py
```

---

## 📊 Features Extracted

The ML system extracts **45+ features** from each land record:

### Price Features (7)
- `price_per_sqm` - Price per square meter
- `price_deviation_ratio` - How far from market value
- `price_below_market` - Boolean: significantly below market
- `price_above_market` - Boolean: significantly above market
- `is_round_price` - Boolean: suspiciously round number
- `price_magnitude` - Log scale of price

### Document Features (6)
- `num_documents` - Total documents provided
- `has_sale_deed`, `has_title_deed`, `has_tax_receipt` - Critical docs
- `missing_critical_docs` - Count of missing critical documents
- `document_completeness` - Score 0-1

### Temporal Features (6)
- `days_since_registration` - How long ago
- `years_since_registration`
- `is_recent_transaction` - Within 6 months
- `registration_year`, `registration_month`
- `registered_on_weekend` - Boolean

### Owner Features (6)
- `owner_name_length` - Character count
- `owner_name_too_short` - Boolean
- `num_owners` - Multiple owners
- `seller_buyer_same` - Boolean: same person
- `has_numbers_in_name`, `has_special_chars`

### Survey/Area Features (6)
- `has_survey_number` - Boolean
- `area_sqm` - Area in square meters
- `area_magnitude` - Log scale
- `is_small_plot`, `is_medium_plot`, `is_large_plot`
- `area_is_round_number`

### Transaction Features (10+)
- `is_sale`, `is_gift`, `is_inheritance`, `is_lease`
- `stamp_duty_paid`, `registration_fee_paid`
- `stamp_duty_ratio` - Compared to expected
- `underpaid_stamp_duty` - Boolean

---

## 🎯 Fraud Signatures

The system learns 5 pre-defined fraud signatures:

### 1. Low Value Suspicious
```
Conditions:
  • Price < 50% of market value
  • Missing 2+ critical documents
  • Area < 100 sqm
Severity: HIGH
```

### 2. Document Fraud
```
Conditions:
  • Missing sale deed OR title deed
  • Underpaid stamp duty
  • Fewer than 2 documents
Severity: HIGH
```

### 3. Identity Fraud
```
Conditions:
  • Seller and buyer have same name
  • Name too short (<3 chars)
  • Numbers or special chars in name
Severity: MEDIUM
```

### 4. Price Manipulation
```
Conditions:
  • Price deviation > 50% from market
  • Round number price
  • Underpaid stamp duty
Severity: HIGH
```

### 5. Gift Deed Fraud
```
Conditions:
  • Transaction type = gift
  • Price below market value
  • Missing 1+ critical documents
Severity: MEDIUM
```

---

## 📈 Model Performance

Expected performance on validation set:

| Metric | Target | Description |
|--------|--------|-------------|
| **Accuracy** | >90% | Overall correctness |
| **Precision** | >85% | Of flagged cases, how many are truly fraud |
| **Recall** | >80% | Of actual fraud, how many are caught |
| **F1 Score** | >85% | Harmonic mean of precision & recall |
| **ROC-AUC** | >0.90 | Area under ROC curve |

### Confusion Matrix (Example)
```
                Predicted
                Normal  Fraud
Actual  Normal    180     5
        Fraud      3      12

Accuracy: 96.0%
Precision: 70.6%  (12 / (12+5))
Recall: 80.0%     (12 / (12+3))
```

---

## 🔧 Integration with Existing Analyzer

### Option 1: Standalone ML Analysis

```python
from ml.ml_pipeline import MLFraudDetectionPipeline

# Load models
pipeline = MLFraudDetectionPipeline()
pipeline.load_models()

# Analyze record
result = pipeline.predict(land_record)
```

### Option 2: Integrated with Analyzer

```python
# In landguard/analyzer/core_analyzer.py

from ml.ml_pipeline import MLFraudDetectionPipeline

class LandRecordAnalyzer:
    def __init__(self):
        # ... existing code ...
        
        # Add ML pipeline
        self.ml_pipeline = None
        self._initialize_ml()
    
    def _initialize_ml(self):
        """Initialize ML pipeline if models exist"""
        try:
            self.ml_pipeline = MLFraudDetectionPipeline()
            self.ml_pipeline.load_models()
            print("✅ ML models loaded")
        except:
            print("⚠️  ML models not found, using rule-based only")
    
    def analyze(self, record: Dict) -> AnalysisResult:
        # Run existing rule-based analysis
        result = self._run_rule_based_analysis(record)
        
        # Add ML predictions if available
        if self.ml_pipeline:
            ml_result = self.ml_pipeline.predict(record)
            
            # Combine results
            result.ml_predictions = ml_result['ml_predictions']
            result.risk_score = ml_result['risk_assessment']['risk_score']
            result.ml_confidence = ml_result['final_verdict']['confidence']
        
        return result
```

### Option 3: CLI Command

```python
# In landguard/cli/main.py

@app.command()
def ml_analyze(
    file: str = typer.Argument(..., help="Input file to analyze"),
    output: str = typer.Option("ml_report.json", help="Output file")
):
    """Run ML-powered fraud detection"""
    
    # Load ML pipeline
    pipeline = MLFraudDetectionPipeline()
    pipeline.load_models()
    
    # Extract record from file
    record = extract_record_from_file(file)
    
    # Predict
    result = pipeline.predict(record, include_explanations=True)
    
    # Display and save
    display_ml_result(result)
    save_result(result, output)
```

Usage:
```bash
python main.py ml-analyze suspicious_deed.pdf --output report.json
```

---

## 🧪 Testing

### Unit Tests

```python
# tests/test_ml.py
import pytest
import numpy as np
from ml.feature_engineering import FeatureEngineer
from ml.anomaly_detector import AnomalyDetector
from ml.fraud_classifier import FraudClassifier

def test_feature_extraction():
    """Test feature engineering"""
    engineer = FeatureEngineer()
    
    record = {
        'owner_name': 'Test Owner',
        'price': 5000000,
        'area': 500,
        'market_value': 5500000,
        # ... other fields
    }
    
    features = engineer.extract_features(record)
    
    assert len(features) > 40
    assert 'price_per_sqm' in features
    assert features['area_sqm'] == 500

def test_anomaly_detection():
    """Test anomaly detector"""
    # Generate normal data
    X_normal = np.random.randn(100, 10)
    
    # Generate anomaly
    X_anomaly = np.array([[10, 10, 10, 10, 10, 10, 10, 10, 10, 10]])
    
    detector = AnomalyDetector()
    detector.fit(X_normal)
    
    is_anomaly, score, _ = detector.predict(X_anomaly)
    
    assert is_anomaly == True
    assert score > 0.5

def test_classifier():
    """Test fraud classifier"""
    # Generate training data
    X = np.random.randn(100, 10)
    y = np.random.randint(0, 2, 100)
    
    classifier = FraudClassifier()
    metrics = classifier.train(X, y)
    
    assert metrics['accuracy'] > 0.5
    assert classifier.is_trained == True

def test_ml_pipeline():
    """Test complete pipeline"""
    from ml.ml_pipeline import MLFraudDetectionPipeline
    
    # Create sample data
    records = [
        {'owner_name': 'Normal', 'price': 5000000, 'area': 500, ...},
        # ... more records
    ]
    labels = [0, 0, 1, ...]  # 0=normal, 1=fraud
    
    pipeline = MLFraudDetectionPipeline()
    pipeline.train(records, labels)
    
    # Test prediction
    test_record = {'owner_name': 'Test', ...}
    result = pipeline.predict(test_record)
    
    assert 'final_verdict' in result
    assert 'risk_assessment' in result
```

Run tests:
```bash
pytest tests/test_ml.py -v
```

---

## 📊 Model Retraining

### When to Retrain

- **Regularly**: Every 3-6 months with new data
- **Performance degradation**: Accuracy drops below 85%
- **New fraud patterns**: Emerging fraud types detected
- **Data drift**: Significant changes in land prices/patterns

### Retraining Script

```python
# scripts/retrain_models.py
from ml.ml_pipeline import MLFraudDetectionPipeline
import pandas as pd
from datetime import datetime

# Load historical data + new data
old_data = pd.read_csv('ml/data/training_data.csv')
new_data = pd.read_csv('ml/data/new_cases_2024.csv')

combined = pd.concat([old_data, new_data])

# Retrain
pipeline = MLFraudDetectionPipeline(models_dir='ml/models')
stats = pipeline.train(
    training_records=combined.to_dict('records'),
    labels=combined['is_fraud'].tolist(),
    fraud_cases=combined[combined['is_fraud']==1].to_dict('records')
)

# Save metadata
metadata = {
    'retrained_at': datetime.now().isoformat(),
    'training_samples': len(combined),
    'fraud_samples': combined['is_fraud'].sum(),
    'metrics': stats
}

with open('ml/models/training_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print("✅ Retraining complete!")
```

---

## 🔍 Explainability

The ML system provides explanations for its predictions:

### 1. Feature Importance
```python
result = pipeline.predict(record)
top_features = result['ml_predictions']['classification']['top_features']

for feat in top_features:
    print(f"{feat['feature']}: {feat['importance']:.3f}")
```

Output:
```
price_deviation_ratio: 0.156
missing_critical_docs: 0.142
seller_buyer_same: 0.128
underpaid_stamp_duty: 0.095
area_sqm: 0.073
```

### 2. Anomaly Reasons
```python
reasons = result['ml_predictions']['anomaly_detection']['reasons']

for reason in reasons:
    print(f"• {reason}")
```

Output:
```
• price_deviation_ratio is unusually high (0.92, z-score: 3.45)
• missing_critical_docs is unusually high (3.00, z-score: 2.87)
• seller_buyer_same is unusually high (1.00, z-score: 2.15)
```

### 3. Pattern Matches
```python
matches = result['ml_predictions']['pattern_matching']['matches']

for match in matches:
    print(f"Signature: {match['signature']}")
    print(f"  Severity: {match['severity']}")
    print(f"  Confidence: {match['confidence']:.1%}")
    print(f"  Match ratio: {match['match_ratio']:.1%}")
```

---

## 🚧 Troubleshooting

### Issue: Models not loading

**Error**: `FileNotFoundError: ml/models/anomaly_detector.pkl`

**Solution**:
```bash
# Check if models exist
ls ml/models/

# If missing, train models first
python scripts/train_models.py
```

### Issue: Low accuracy

**Problem**: Accuracy < 80%

**Solutions**:
1. **More training data**: Need 200+ samples minimum
2. **Balance dataset**: Equal fraud/normal cases
3. **Feature engineering**: Add domain-specific features
4. **Hyperparameter tuning**:
   ```python
   classifier = FraudClassifier()
   classifier.model.set_params(
       n_estimators=300,
       max_depth=15,
       min_samples_split=3
   )
   ```

### Issue: Overfitting

**Symptoms**: Training accuracy 99%, validation accuracy 70%

**Solutions**:
1. **Reduce model complexity**:
   ```python
   classifier.model.set_params(max_depth=8)
   ```
2. **More data**: Collect more diverse examples
3. **Cross-validation**: Use k-fold CV
4. **Regularization**: Add class weights

### Issue: Slow predictions

**Problem**: Takes >5 seconds per record

**Solutions**:
1. **Batch processing**:
   ```python
   results = pipeline.batch_predict(records)
   ```
2. **Feature caching**:
   ```python
   # Pre-extract features
   features = [engineer.extract_features(r) for r in records]
   ```
3. **Model optimization**: Use simpler models

---

## 📈 Next Steps

### Enhancements

1. **Deep Learning Models**
   - Neural networks for complex patterns
   - LSTM for temporal sequences
   - Autoencoders for anomaly detection

2. **Advanced Feature Engineering**
   - NLP on document text
   - Image analysis of scanned documents
   - Graph features (ownership networks)

3. **Active Learning**
   - Learn from user feedback
   - Continuous model updates
   - Uncertainty sampling

4. **Model Interpretability**
   - SHAP values for explanations
   - LIME for local interpretability
   - Counterfactual explanations

5. **Deployment**
   - REST API for predictions
   - Real-time fraud detection
   - Model versioning
   - A/B testing

---

## 📚 References

- **Scikit-learn Documentation**: https://scikit-learn.org/
- **Isolation Forest Paper**: Liu et al. (2008)
- **Random Forest**: Breiman (2001)
- **Fraud Detection**: Bolton & Hand (2002)

---

## 🎉 Success Metrics

After implementing Phase 7, you should achieve:

✅ **90%+ fraud detection accuracy**
✅ **<5% false positive rate**
✅ **Explainable predictions** (know why it's flagged)
✅ **Fast predictions** (<1 second per record)
✅ **Continuous learning** from new cases

---

## 💡 Tips

1. **Start simple**: Train on small dataset first
2. **Validate constantly**: Check predictions manually
3. **Domain expertise**: Work with land registry experts
4. **Iterate**: Improve features based on errors
5. **Monitor performance**: Track accuracy over time

---

**Phase 7 Complete! 🎉**

Your LandGuard system now has intelligent fraud detection powered by machine learning.

**Next Phase**: Phase 4 (Advanced Reporting) or Phase 5 (Blockchain/IPFS)

**Questions?** Open an issue or contact the team!