from ml_pipeline import MLFraudDetectionPipeline
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