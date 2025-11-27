# scripts/predict_fraud.py
from ml_pipeline import MLFraudDetectionPipeline
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