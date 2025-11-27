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

