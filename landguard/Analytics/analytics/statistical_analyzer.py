"""
LandGuard Statistical Analytics
Comprehensive statistical analysis of fraud patterns
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
from collections import Counter, defaultdict
from scipy import stats


class StatisticalAnalyzer:
    """Perform statistical analysis on fraud detection data"""
    
    def __init__(self, data_source: str = None):
        """
        Initialize statistical analyzer
        
        Args:
            data_source: Path to data directory (audit logs, evidence, etc.)
        """
        self.data_source = Path(data_source) if data_source else Path('Blockchain/blockchain/blockchain/storage')
        self.analysis_cache = {}
    
    def load_fraud_cases(self) -> pd.DataFrame:
        """
        Load all fraud cases from evidence storage
        
        Returns:
            DataFrame with fraud case data
        """
        evidence_dir = self.data_source / 'evidence'
        
        if not evidence_dir.exists():
            return pd.DataFrame()
        
        cases = []
        
        for file_path in evidence_dir.glob('*_complete.json'):
            try:
                with open(file_path, 'r') as f:
                    package = json.load(f)
                    evidence = package.get('evidence', {})
                    analysis = evidence.get('analysis_result', {})
                    
                    case = {
                        'record_id': evidence.get('record_id'),
                        'timestamp': evidence.get('timestamp'),
                        'is_fraudulent': analysis.get('is_fraudulent', False),
                        'risk_score': analysis.get('risk_score', 0),
                        'confidence': analysis.get('confidence', 0),
                        'fraud_indicators': len(analysis.get('fraud_indicators', [])),
                        'evidence_hash': package.get('integrity', {}).get('evidence_hash')
                    }
                    
                    # Add ML predictions if available
                    ml_pred = evidence.get('ml_predictions', {})
                    if ml_pred:
                        case['anomaly_score'] = ml_pred.get('anomaly_score', 0)
                        case['classifier_probability'] = ml_pred.get('classifier_probability', 0)
                        case['pattern_matches'] = ml_pred.get('pattern_matches', 0)
                    
                    cases.append(case)
            
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
        
        df = pd.DataFrame(cases)
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['month'] = df['timestamp'].dt.month
        
        return df
    
    def compute_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Compute comprehensive summary statistics
        
        Args:
            df: DataFrame with fraud cases
        
        Returns:
            Dictionary with summary statistics
        """
        if df.empty:
            return {'error': 'No data available'}
        
        stats_summary = {
            'overview': {
                'total_cases': len(df),
                'fraud_cases': int(df['is_fraudulent'].sum()),
                'normal_cases': int((~df['is_fraudulent']).sum()),
                'fraud_rate': float(df['is_fraudulent'].mean()),
                'date_range': {
                    'start': str(df['timestamp'].min()) if 'timestamp' in df.columns else None,
                    'end': str(df['timestamp'].max()) if 'timestamp' in df.columns else None
                }
            },
            'risk_scores': {
                'mean': float(df['risk_score'].mean()),
                'median': float(df['risk_score'].median()),
                'std': float(df['risk_score'].std()),
                'min': float(df['risk_score'].min()),
                'max': float(df['risk_score'].max()),
                'quartiles': {
                    'q1': float(df['risk_score'].quantile(0.25)),
                    'q2': float(df['risk_score'].quantile(0.50)),
                    'q3': float(df['risk_score'].quantile(0.75))
                }
            }
        }
        
        # Fraud-specific statistics
        fraud_df = df[df['is_fraudulent'] == True]
        
        if not fraud_df.empty:
            stats_summary['fraud_statistics'] = {
                'avg_risk_score': float(fraud_df['risk_score'].mean()),
                'avg_confidence': float(fraud_df['confidence'].mean()) if 'confidence' in fraud_df.columns else 0,
                'avg_indicators': float(fraud_df['fraud_indicators'].mean()) if 'fraud_indicators' in fraud_df.columns else 0
            }
            
            # ML statistics
            if 'anomaly_score' in fraud_df.columns:
                stats_summary['ml_statistics'] = {
                    'avg_anomaly_score': float(fraud_df['anomaly_score'].mean()),
                    'avg_classifier_prob': float(fraud_df['classifier_probability'].mean()) if 'classifier_probability' in fraud_df.columns else 0,
                    'avg_pattern_matches': float(fraud_df['pattern_matches'].mean()) if 'pattern_matches' in fraud_df.columns else 0
                }
        
        return stats_summary
    
    def analyze_temporal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze fraud patterns over time
        
        Args:
            df: DataFrame with fraud cases
        
        Returns:
            Temporal pattern analysis
        """
        if df.empty or 'timestamp' not in df.columns:
            return {'error': 'No temporal data available'}
        
        fraud_df = df[df['is_fraudulent'] == True]
        
        temporal_analysis = {
            'by_hour': {},
            'by_day_of_week': {},
            'by_month': {},
            'trends': {}
        }
        
        # Hourly pattern
        if 'hour' in fraud_df.columns:
            hourly = fraud_df.groupby('hour').size()
            temporal_analysis['by_hour'] = {
                int(hour): int(count) for hour, count in hourly.items()
            }
            
            # Find peak hours
            if not hourly.empty:
                peak_hour = int(hourly.idxmax())
                temporal_analysis['peak_hour'] = {
                    'hour': peak_hour,
                    'cases': int(hourly.max())
                }
        
        # Day of week pattern
        if 'day_of_week' in fraud_df.columns:
            dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily = fraud_df.groupby('day_of_week').size()
            temporal_analysis['by_day_of_week'] = {
                dow_names[int(day)]: int(count) for day, count in daily.items()
            }
        
        # Monthly pattern
        if 'month' in fraud_df.columns:
            monthly = fraud_df.groupby('month').size()
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            temporal_analysis['by_month'] = {
                month_names[int(month)-1]: int(count) for month, count in monthly.items()
            }
        
        # Trend analysis
        if 'date' in fraud_df.columns:
            daily_counts = fraud_df.groupby('date').size()
            
            if len(daily_counts) >= 7:
                # Calculate moving averages
                ma_7 = daily_counts.rolling(window=7).mean()
                ma_30 = daily_counts.rolling(window=30).mean() if len(daily_counts) >= 30 else None
                
                temporal_analysis['trends'] = {
                    'daily_average': float(daily_counts.mean()),
                    'weekly_average': float(ma_7.mean()),
                    'trend_direction': 'increasing' if daily_counts.iloc[-7:].mean() > daily_counts.iloc[:7].mean() else 'decreasing'
                }
        
        return temporal_analysis
    
    def detect_outliers(self, df: pd.DataFrame, column: str = 'risk_score') -> Dict[str, Any]:
        """
        Detect statistical outliers using Z-score and IQR methods
        
        Args:
            df: DataFrame with fraud cases
            column: Column to analyze for outliers
        
        Returns:
            Outlier detection results
        """
        if df.empty or column not in df.columns:
            return {'error': f'Column {column} not found'}
        
        data = df[column].dropna()
        
        # Z-score method
        z_scores = np.abs(stats.zscore(data))
        z_outliers = data[z_scores > 3]
        
        # IQR method
        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        iqr_outliers = data[(data < lower_bound) | (data > upper_bound)]
        
        return {
            'z_score_method': {
                'num_outliers': len(z_outliers),
                'outlier_values': z_outliers.tolist() if len(z_outliers) < 20 else z_outliers.head(20).tolist(),
                'threshold': 3.0
            },
            'iqr_method': {
                'num_outliers': len(iqr_outliers),
                'outlier_values': iqr_outliers.tolist() if len(iqr_outliers) < 20 else iqr_outliers.head(20).tolist(),
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound),
                'iqr': float(iqr)
            },
            'statistics': {
                'mean': float(data.mean()),
                'median': float(data.median()),
                'std': float(data.std()),
                'min': float(data.min()),
                'max': float(data.max())
            }
        }
    
    def analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze correlations between features
        
        Args:
            df: DataFrame with fraud cases
        
        Returns:
            Correlation analysis
        """
        if df.empty:
            return {'error': 'No data available'}
        
        # Select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) < 2:
            return {'error': 'Insufficient numeric columns'}
        
        # Compute correlation matrix
        corr_matrix = df[numeric_cols].corr()
        
        # Find strong correlations (|r| > 0.7)
        strong_correlations = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]
                
                if abs(corr_value) > 0.7:
                    strong_correlations.append({
                        'feature_1': col1,
                        'feature_2': col2,
                        'correlation': float(corr_value),
                        'strength': 'strong positive' if corr_value > 0 else 'strong negative'
                    })
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'strong_correlations': strong_correlations,
            'features_analyzed': numeric_cols
        }
    
    def perform_hypothesis_tests(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform statistical hypothesis tests
        
        Args:
            df: DataFrame with fraud cases
        
        Returns:
            Hypothesis test results
        """
        if df.empty or 'is_fraudulent' not in df.columns:
            return {'error': 'Insufficient data'}
        
        results = {}
        
        # Test 1: Risk score difference between fraud and normal
        fraud_scores = df[df['is_fraudulent'] == True]['risk_score']
        normal_scores = df[df['is_fraudulent'] == False]['risk_score']
        
        if len(fraud_scores) > 0 and len(normal_scores) > 0:
            t_stat, p_value = stats.ttest_ind(fraud_scores, normal_scores)
            
            results['risk_score_difference'] = {
                'test': 'Independent T-Test',
                'hypothesis': 'Fraud cases have higher risk scores',
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05,
                'fraud_mean': float(fraud_scores.mean()),
                'normal_mean': float(normal_scores.mean()),
                'conclusion': 'Significant difference' if p_value < 0.05 else 'No significant difference'
            }
        
        # Test 2: Chi-square for temporal patterns
        if 'day_of_week' in df.columns:
            contingency_table = pd.crosstab(df['day_of_week'], df['is_fraudulent'])
            chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
            
            results['temporal_independence'] = {
                'test': 'Chi-Square Test',
                'hypothesis': 'Fraud occurrence is independent of day of week',
                'chi2_statistic': float(chi2),
                'p_value': float(p_value),
                'degrees_of_freedom': int(dof),
                'significant': p_value < 0.05,
                'conclusion': 'Not independent' if p_value < 0.05 else 'Independent'
            }
        
        return results
    
    def generate_report(self, output_path: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive statistical report
        
        Args:
            output_path: Path to save report JSON
        
        Returns:
            Complete statistical report
        """
        print("📊 Generating Statistical Analysis Report...\n")
        
        # Load data
        df = self.load_fraud_cases()
        
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        print(f"✅ Loaded {len(df)} cases ({df['is_fraudulent'].sum()} fraud)")
        
        # Perform all analyses
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'data_summary': {
                'total_cases': len(df),
                'fraud_cases': int(df['is_fraudulent'].sum()),
                'date_range': {
                    'start': str(df['timestamp'].min()) if 'timestamp' in df.columns else None,
                    'end': str(df['timestamp'].max()) if 'timestamp' in df.columns else None
                }
            },
            'summary_statistics': self.compute_summary_statistics(df),
            'temporal_patterns': self.analyze_temporal_patterns(df),
            'outlier_analysis': self.detect_outliers(df),
            'correlation_analysis': self.analyze_correlations(df),
            'hypothesis_tests': self.perform_hypothesis_tests(df)
        }
        
        # Save report
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"\n💾 Report saved to: {output_path}")
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print human-readable summary of statistical analysis"""
        print("\n" + "="*70)
        print("📊 STATISTICAL ANALYSIS SUMMARY")
        print("="*70)
        
        # Overview
        overview = report['summary_statistics']['overview']
        print(f"\n📈 Overview:")
        print(f"   Total Cases: {overview['total_cases']}")
        print(f"   Fraud Cases: {overview['fraud_cases']} ({overview['fraud_rate']:.1%})")
        print(f"   Normal Cases: {overview['normal_cases']}")
        
        # Risk Scores
        risk = report['summary_statistics']['risk_scores']
        print(f"\n📊 Risk Score Statistics:")
        print(f"   Mean: {risk['mean']:.2f}")
        print(f"   Median: {risk['median']:.2f}")
        print(f"   Std Dev: {risk['std']:.2f}")
        print(f"   Range: {risk['min']:.2f} - {risk['max']:.2f}")
        
        # Temporal Patterns
        if 'peak_hour' in report['temporal_patterns']:
            peak = report['temporal_patterns']['peak_hour']
            print(f"\n⏰ Temporal Patterns:")
            print(f"   Peak Hour: {peak['hour']}:00 ({peak['cases']} cases)")
        
        # Outliers
        outliers = report['outlier_analysis']
        if 'z_score_method' in outliers:
            print(f"\n🔍 Outliers Detected:")
            print(f"   Z-Score Method: {outliers['z_score_method']['num_outliers']} outliers")
            print(f"   IQR Method: {outliers['iqr_method']['num_outliers']} outliers")
        
        # Strong Correlations
        corr = report['correlation_analysis']
        if 'strong_correlations' in corr and corr['strong_correlations']:
            print(f"\n🔗 Strong Correlations:")
            for c in corr['strong_correlations'][:3]:
                print(f"   {c['feature_1']} ↔ {c['feature_2']}: {c['correlation']:.3f}")
        
        print("\n" + "="*70)


# Example usage
if __name__ == "__main__":
    print("📊 LandGuard Statistical Analysis Demo\n")
    
    # Initialize analyzer
    analyzer = StatisticalAnalyzer('blockchain/storage')
    
    # Generate comprehensive report
    report = analyzer.generate_report('analytics/outputs/reports/statistical_report.json')
    
    # Print summary
    analyzer.print_summary(report)
    
    print("\n✅ Statistical Analysis Complete!")