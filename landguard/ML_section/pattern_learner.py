"""
LandGuard Pattern Learning & Risk Scoring
Learn fraud signatures and calculate comprehensive risk scores
"""

import numpy as np
import json
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
from datetime import datetime
from pathlib import Path


class FraudPatternLearner:
    """Learn and recognize fraud patterns from historical data"""
    
    def __init__(self):
        self.patterns = {
            'price_patterns': [],
            'document_patterns': [],
            'temporal_patterns': [],
            'owner_patterns': [],
            'combined_patterns': []
        }
        
        self.fraud_signatures = []
        self.pattern_frequencies = defaultdict(int)
        self.is_trained = False
    
    def learn_patterns(self, fraud_records: List[Dict], 
                      normal_records: List[Dict] = None):
        """
        Learn fraud patterns from historical fraud cases
        
        Args:
            fraud_records: List of confirmed fraud cases
            normal_records: List of normal cases (for contrast)
        """
        print(f"🧠 Learning fraud patterns from {len(fraud_records)} fraud cases...")
        
        # Learn price-based patterns
        self._learn_price_patterns(fraud_records, normal_records)
        
        # Learn document patterns
        self._learn_document_patterns(fraud_records, normal_records)
        
        # Learn temporal patterns
        self._learn_temporal_patterns(fraud_records)
        
        # Learn owner patterns
        self._learn_owner_patterns(fraud_records)
        
        # Generate combined signatures
        self._generate_fraud_signatures(fraud_records)
        
        self.is_trained = True
        print("✅ Pattern learning complete!")
        print(f"   Learned {len(self.fraud_signatures)} fraud signatures")
    
    def _learn_price_patterns(self, fraud_records: List[Dict], 
                             normal_records: List[Dict] = None):
        """Learn price-related fraud patterns"""
        patterns = []
        
        for record in fraud_records:
            price = record.get('price', 0)
            market_value = record.get('market_value', 0)
            
            if market_value > 0:
                deviation_ratio = abs(price - market_value) / market_value
                
                if deviation_ratio > 0.5:
                    patterns.append({
                        'type': 'large_price_deviation',
                        'deviation_ratio': deviation_ratio,
                        'threshold': 0.5
                    })
                
                if price < market_value * 0.5:
                    patterns.append({
                        'type': 'suspiciously_low_price',
                        'price_ratio': price / market_value,
                        'threshold': 0.5
                    })
        
        self.patterns['price_patterns'] = patterns
        print(f"   📊 Learned {len(patterns)} price patterns")
    
    def _learn_document_patterns(self, fraud_records: List[Dict], 
                                normal_records: List[Dict] = None):
        """Learn document-related fraud patterns"""
        patterns = []
        
        # Count missing documents in fraud cases
        missing_docs_counter = Counter()
        
        critical_docs = ['sale_deed', 'title_deed', 'encumbrance_certificate', 
                        'tax_receipt', 'survey_map']
        
        for record in fraud_records:
            documents = [str(d).lower() for d in record.get('documents', [])]
            
            for critical_doc in critical_docs:
                if not any(critical_doc.replace('_', ' ') in doc for doc in documents):
                    missing_docs_counter[critical_doc] += 1
        
        # Pattern: frequently missing documents in fraud cases
        total_fraud = len(fraud_records)
        for doc, count in missing_docs_counter.most_common():
            frequency = count / total_fraud
            if frequency > 0.3:  # Missing in >30% of fraud cases
                patterns.append({
                    'type': 'frequently_missing_document',
                    'document': doc,
                    'frequency': frequency,
                    'missing_count': count
                })
        
        self.patterns['document_patterns'] = patterns
        print(f"   📄 Learned {len(patterns)} document patterns")
    
    def _learn_temporal_patterns(self, fraud_records: List[Dict]):
        """Learn time-based fraud patterns"""
        patterns = []
        
        # Analyze registration dates
        months = []
        weekdays = []
        
        for record in fraud_records:
            date_str = record.get('registration_date', '')
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                months.append(date.month)
                weekdays.append(date.weekday())
            except:
                continue
        
        if months:
            # Find most common fraud months
            month_counts = Counter(months)
            total = len(months)
            
            for month, count in month_counts.most_common(3):
                frequency = count / total
                if frequency > 0.15:  # Appears in >15% of cases
                    patterns.append({
                        'type': 'high_fraud_month',
                        'month': month,
                        'frequency': frequency
                    })
        
        if weekdays:
            # Check for weekend registrations
            weekend_count = sum(1 for w in weekdays if w >= 5)
            weekend_ratio = weekend_count / len(weekdays)
            
            if weekend_ratio > 0.2:  # >20% on weekends
                patterns.append({
                    'type': 'frequent_weekend_registration',
                    'weekend_ratio': weekend_ratio
                })
        
        self.patterns['temporal_patterns'] = patterns
        print(f"   📅 Learned {len(patterns)} temporal patterns")
    
    def _learn_owner_patterns(self, fraud_records: List[Dict]):
        """Learn owner-related fraud patterns"""
        patterns = []
        
        # Check for seller-buyer same name pattern
        same_name_count = 0
        total = len(fraud_records)
        
        for record in fraud_records:
            owner = record.get('owner_name', '').lower()
            seller = record.get('seller_name', '').lower()
            
            if owner and seller and owner == seller:
                same_name_count += 1
        
        if same_name_count / total > 0.1:  # Appears in >10% of fraud
            patterns.append({
                'type': 'seller_buyer_same_name',
                'frequency': same_name_count / total
            })
        
        # Check for suspicious name patterns
        short_names = sum(1 for r in fraud_records if len(r.get('owner_name', '')) < 3)
        if short_names / total > 0.15:
            patterns.append({
                'type': 'unusually_short_names',
                'frequency': short_names / total
            })
        
        self.patterns['owner_patterns'] = patterns
        print(f"   👤 Learned {len(patterns)} owner patterns")
    
    def _generate_fraud_signatures(self, fraud_records: List[Dict]):
        """Generate high-level fraud signatures from patterns"""
        signatures = []
        
        # Signature 1: Low-value suspicious transaction
        signatures.append({
            'name': 'low_value_suspicious',
            'conditions': [
                'price < market_value * 0.5',
                'missing_critical_docs >= 2',
                'area < 100'
            ],
            'severity': 'high',
            'confidence': 0.85
        })
        
        # Signature 2: Document fraud
        signatures.append({
            'name': 'document_fraud',
            'conditions': [
                'missing_sale_deed OR missing_title_deed',
                'underpaid_stamp_duty',
                'num_documents < 2'
            ],
            'severity': 'high',
            'confidence': 0.80
        })
        
        # Signature 3: Identity fraud
        signatures.append({
            'name': 'identity_fraud',
            'conditions': [
                'seller_buyer_same_name',
                'owner_name_too_short',
                'has_numbers_in_name OR has_special_chars'
            ],
            'severity': 'medium',
            'confidence': 0.70
        })
        
        # Signature 4: Price manipulation
        signatures.append({
            'name': 'price_manipulation',
            'conditions': [
                'price_deviation_ratio > 0.5',
                'is_round_price',
                'underpaid_stamp_duty'
            ],
            'severity': 'high',
            'confidence': 0.75
        })
        
        # Signature 5: Gift deed fraud
        signatures.append({
            'name': 'gift_deed_fraud',
            'conditions': [
                'transaction_type == gift',
                'price_below_market',
                'missing_critical_docs >= 1'
            ],
            'severity': 'medium',
            'confidence': 0.65
        })
        
        self.fraud_signatures = signatures
    
    def match_patterns(self, record: Dict, features: Dict) -> List[Dict]:
        """
        Match a record against learned fraud patterns
        
        Args:
            record: Raw record data
            features: Extracted features
        
        Returns:
            List of matched patterns with details
        """
        matched = []
        
        for signature in self.fraud_signatures:
            matches = self._check_signature(signature, record, features)
            if matches['matched']:
                matched.append({
                    'signature': signature['name'],
                    'severity': signature['severity'],
                    'confidence': signature['confidence'],
                    'matched_conditions': matches['conditions'],
                    'match_ratio': matches['match_ratio']
                })
        
        return matched
    
    def _check_signature(self, signature: Dict, record: Dict, 
                        features: Dict) -> Dict:
        """Check if a signature matches"""
        conditions = signature['conditions']
        matched_conditions = []
        
        for condition in conditions:
            if self._evaluate_condition(condition, record, features):
                matched_conditions.append(condition)
        
        match_ratio = len(matched_conditions) / len(conditions)
        is_matched = match_ratio >= 0.6  # Need 60% of conditions
        
        return {
            'matched': is_matched,
            'conditions': matched_conditions,
            'match_ratio': match_ratio
        }
    
    def _evaluate_condition(self, condition: str, record: Dict, 
                          features: Dict) -> bool:
        """Evaluate a single condition"""
        # Simple condition evaluation
        # In production, use a proper expression evaluator
        
        if 'price < market_value' in condition:
            price = record.get('price', 0)
            market = record.get('market_value', 0)
            if '*' in condition:
                factor = float(condition.split('*')[1].strip())
                return price < market * factor
            return price < market
        
        if 'missing_critical_docs' in condition:
            threshold = int(condition.split('>=')[1].strip())
            return features.get('missing_critical_docs', 0) >= threshold
        
        if 'area <' in condition:
            threshold = int(condition.split('<')[1].strip())
            return features.get('area_sqm', 0) < threshold
        
        if 'seller_buyer_same_name' in condition:
            return features.get('seller_buyer_same', 0) == 1.0
        
        if 'owner_name_too_short' in condition:
            return features.get('owner_name_too_short', 0) == 1.0
        
        if 'underpaid_stamp_duty' in condition:
            return features.get('underpaid_stamp_duty', 0) == 1.0
        
        if 'price_deviation_ratio' in condition:
            threshold = float(condition.split('>')[1].strip())
            return features.get('price_deviation_ratio', 0) > threshold
        
        if 'transaction_type == gift' in condition:
            return features.get('is_gift', 0) == 1.0
        
        return False
    
    def save(self, path: str):
        """Save learned patterns"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'patterns': self.patterns,
            'fraud_signatures': self.fraud_signatures,
            'is_trained': self.is_trained
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Patterns saved to {path}")
    
    @classmethod
    def load(cls, path: str):
        """Load learned patterns"""
        with open(path, 'r') as f:
            data = json.load(f)
        
        learner = cls()
        learner.patterns = data['patterns']
        learner.fraud_signatures = data['fraud_signatures']
        learner.is_trained = data['is_trained']
        
        print(f"📂 Patterns loaded from {path}")
        return learner


class RiskScorer:
    """Calculate comprehensive risk scores"""
    
    def __init__(self, pattern_learner: FraudPatternLearner = None):
        self.pattern_learner = pattern_learner
        
        # Risk weights for different components
        self.weights = {
            'anomaly_score': 0.25,
            'classifier_probability': 0.30,
            'pattern_match_score': 0.25,
            'rule_based_score': 0.20
        }
    
    def calculate_risk_score(self, 
                            anomaly_score: float = None,
                            classifier_prob: float = None,
                            pattern_matches: List[Dict] = None,
                            rule_violations: List[Dict] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score (0-100)
        
        Args:
            anomaly_score: Score from anomaly detector (0-1)
            classifier_prob: Probability from classifier (0-1)
            pattern_matches: Matched fraud patterns
            rule_violations: Violated rules from analyzer
        
        Returns:
            Dictionary with risk score and breakdown
        """
        scores = {}
        
        # Anomaly score component
        if anomaly_score is not None:
            scores['anomaly'] = anomaly_score * 100
        else:
            scores['anomaly'] = 0
        
        # Classifier component
        if classifier_prob is not None:
            scores['classifier'] = classifier_prob * 100
        else:
            scores['classifier'] = 0
        
        # Pattern matching component
        if pattern_matches:
            # Weight by severity and confidence
            pattern_score = 0
            for match in pattern_matches:
                severity_weight = {'high': 1.0, 'medium': 0.7, 'low': 0.4}
                weight = severity_weight.get(match['severity'], 0.5)
                pattern_score += weight * match['confidence'] * match['match_ratio']
            
            scores['patterns'] = min(pattern_score * 100, 100)
        else:
            scores['patterns'] = 0
        
        # Rule-based component
        if rule_violations:
            # Count high/medium/low severity rules
            severity_counts = {'high': 0, 'medium': 0, 'low': 0}
            for rule in rule_violations:
                severity = rule.get('severity', 'low')
                severity_counts[severity] += 1
            
            rule_score = (
                severity_counts['high'] * 30 +
                severity_counts['medium'] * 15 +
                severity_counts['low'] * 5
            )
            scores['rules'] = min(rule_score, 100)
        else:
            scores['rules'] = 0
        
        # Calculate weighted final score
        final_score = (
            scores['anomaly'] * self.weights['anomaly_score'] +
            scores['classifier'] * self.weights['classifier_probability'] +
            scores['patterns'] * self.weights['pattern_match_score'] +
            scores['rules'] * self.weights['rule_based_score']
        )
        
        # Risk categorization
        if final_score >= 75:
            risk_level = 'CRITICAL'
            color = '🔴'
        elif final_score >= 50:
            risk_level = 'HIGH'
            color = '🟠'
        elif final_score >= 25:
            risk_level = 'MEDIUM'
            color = '🟡'
        else:
            risk_level = 'LOW'
            color = '🟢'
        
        return {
            'risk_score': round(final_score, 2),
            'risk_level': risk_level,
            'risk_color': color,
            'component_scores': scores,
            'weights': self.weights,
            'interpretation': self._interpret_score(final_score)
        }
    
    def _interpret_score(self, score: float) -> str:
        """Interpret risk score"""
        if score >= 75:
            return "Critical fraud risk - immediate investigation required"
        elif score >= 50:
            return "High fraud risk - thorough verification needed"
        elif score >= 25:
            return "Moderate fraud risk - additional checks recommended"
        else:
            return "Low fraud risk - standard processing acceptable"


# Example usage
if __name__ == "__main__":
    print("🧠 Pattern Learning Example\n")
    
    # Sample fraud cases
    fraud_cases = [
        {
            'owner_name': 'X',
            'seller_name': 'X',
            'price': 100000,
            'market_value': 5000000,
            'area': 50,
            'documents': ['sale_deed'],
            'registration_date': '2024-12-25',
            'transaction_type': 'gift',
            'stamp_duty': 1000
        },
        {
            'owner_name': 'ABC',
            'seller_name': 'ABC',
            'price': 200000,
            'market_value': 4000000,
            'area': 80,
            'documents': [],
            'registration_date': '2024-07-04',
            'transaction_type': 'sale',
            'stamp_duty': 2000
        }
    ]
    
    # Learn patterns
    learner = FraudPatternLearner()
    learner.learn_patterns(fraud_cases)
    
    # Test risk scoring
    print("\n📊 Risk Scoring Example\n")
    
    scorer = RiskScorer(learner)
    risk_result = scorer.calculate_risk_score(
        anomaly_score=0.85,
        classifier_prob=0.92,
        pattern_matches=[
            {'severity': 'high', 'confidence': 0.85, 'match_ratio': 0.8}
        ],
        rule_violations=[
            {'severity': 'high'}, {'severity': 'medium'}, {'severity': 'low'}
        ]
    )
    
    print(f"{risk_result['risk_color']} Risk Score: {risk_result['risk_score']}/100")
    print(f"   Risk Level: {risk_result['risk_level']}")
    print(f"   {risk_result['interpretation']}")
    print(f"\n   Component Breakdown:")
    for component, score in risk_result['component_scores'].items():
        print(f"      {component:12s}: {score:.2f}")
    
    # Save patterns
    learner.save('ml/data/fraud_patterns.json')