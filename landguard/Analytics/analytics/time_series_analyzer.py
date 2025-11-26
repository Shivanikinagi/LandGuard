"""
LandGuard Time-Series Analysis
Analyze fraud trends and patterns over time
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats


class TimeSeriesAnalyzer:
    """Analyze temporal patterns and trends in fraud data"""
    
    def __init__(self, output_dir: str = 'analytics/outputs/reports'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        sns.set_style('darkgrid')
        plt.rcParams['figure.figsize'] = (12, 6)
    
    def load_time_series_data(self, data_source: str = 'blockchain/storage') -> pd.DataFrame:
        """
        Load fraud data with timestamps
        
        Args:
            data_source: Path to data directory
        
        Returns:
            DataFrame with time-series data
        """
        evidence_dir = Path(data_source) / 'evidence'
        
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
                        'confidence': analysis.get('confidence', 0)
                    }
                    
                    cases.append(case)
            
            except Exception as e:
                continue
        
        df = pd.DataFrame(cases)
        
        if 'timestamp' in df.columns and not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            df['date'] = df['timestamp'].dt.date
            df['week'] = df['timestamp'].dt.to_period('W')
            df['month'] = df['timestamp'].dt.to_period('M')
            df['day_of_week'] = df['timestamp'].dt.day_name()
            df['hour'] = df['timestamp'].dt.hour
        
        return df
    
    def calculate_fraud_rate_over_time(self, df: pd.DataFrame, 
                                       period: str = 'D') -> pd.DataFrame:
        """
        Calculate fraud rate over time
        
        Args:
            df: DataFrame with time-series data
            period: Pandas period ('D'=day, 'W'=week, 'M'=month)
        
        Returns:
            DataFrame with fraud rates
        """
        if df.empty or 'timestamp' not in df.columns:
            return pd.DataFrame()
        
        # Resample by period
        fraud_series = df.set_index('timestamp').resample(period).agg({
            'is_fraudulent': ['sum', 'count', 'mean']
        })
        
        fraud_series.columns = ['fraud_count', 'total_count', 'fraud_rate']
        fraud_series = fraud_series.reset_index()
        
        return fraud_series
    
    def detect_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect trends using linear regression
        
        Args:
            df: DataFrame with time-series data
        
        Returns:
            Trend analysis results
        """
        if df.empty or 'timestamp' not in df.columns:
            return {'error': 'No temporal data'}
        
        # Daily fraud rate
        daily_fraud = self.calculate_fraud_rate_over_time(df, 'D')
        
        if len(daily_fraud) < 7:
            return {'error': 'Insufficient data for trend analysis'}
        
        # Prepare data for regression
        daily_fraud['days_since_start'] = (daily_fraud['timestamp'] - daily_fraud['timestamp'].min()).dt.days
        
        X = daily_fraud['days_since_start'].values
        y = daily_fraud['fraud_rate'].values
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
        
        # Determine trend
        if p_value < 0.05:
            if slope > 0:
                trend = 'increasing'
                interpretation = 'Fraud rate is significantly increasing over time'
            else:
                trend = 'decreasing'
                interpretation = 'Fraud rate is significantly decreasing over time'
        else:
            trend = 'stable'
            interpretation = 'No significant trend detected'
        
        # Calculate moving averages
        daily_fraud['ma_7'] = daily_fraud['fraud_rate'].rolling(window=7).mean()
        daily_fraud['ma_30'] = daily_fraud['fraud_rate'].rolling(window=30).mean() if len(daily_fraud) >= 30 else None
        
        return {
            'trend': trend,
            'slope': float(slope),
            'r_squared': float(r_value ** 2),
            'p_value': float(p_value),
            'interpretation': interpretation,
            'current_rate': float(daily_fraud['fraud_rate'].iloc[-1]),
            'avg_rate_last_7_days': float(daily_fraud['fraud_rate'].iloc[-7:].mean()) if len(daily_fraud) >= 7 else None,
            'avg_rate_last_30_days': float(daily_fraud['fraud_rate'].iloc[-30:].mean()) if len(daily_fraud) >= 30 else None
        }
    
    def detect_seasonality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect seasonal patterns
        
        Args:
            df: DataFrame with time-series data
        
        Returns:
            Seasonality analysis
        """
        if df.empty or 'timestamp' not in df.columns:
            return {'error': 'No temporal data'}
        
        fraud_df = df[df['is_fraudulent'] == True]
        
        seasonality = {}
        
        # Day of week seasonality
        if 'day_of_week' in fraud_df.columns:
            dow_counts = fraud_df['day_of_week'].value_counts()
            seasonality['day_of_week'] = {
                'pattern': dow_counts.to_dict(),
                'peak_day': dow_counts.idxmax(),
                'peak_count': int(dow_counts.max())
            }
        
        # Hourly seasonality
        if 'hour' in fraud_df.columns:
            hour_counts = fraud_df['hour'].value_counts().sort_index()
            seasonality['hourly'] = {
                'pattern': hour_counts.to_dict(),
                'peak_hour': int(hour_counts.idxmax()),
                'peak_count': int(hour_counts.max())
            }
        
        # Monthly seasonality
        if 'month' in fraud_df.columns:
            month_counts = fraud_df['month'].value_counts().sort_index()
            seasonality['monthly'] = {
                'pattern': {str(k): int(v) for k, v in month_counts.items()},
                'peak_month': str(month_counts.idxmax()),
                'peak_count': int(month_counts.max())
            }
        
        return seasonality
    
    def forecast_future_fraud(self, df: pd.DataFrame, 
                             days_ahead: int = 30) -> Dict[str, Any]:
        """
        Simple linear forecast of fraud rate
        
        Args:
            df: DataFrame with time-series data
            days_ahead: Number of days to forecast
        
        Returns:
            Forecast results
        """
        if df.empty or 'timestamp' not in df.columns:
            return {'error': 'No temporal data'}
        
        # Daily fraud rate
        daily_fraud = self.calculate_fraud_rate_over_time(df, 'D')
        
        if len(daily_fraud) < 7:
            return {'error': 'Insufficient data for forecasting'}
        
        # Prepare data
        daily_fraud['days_since_start'] = (daily_fraud['timestamp'] - daily_fraud['timestamp'].min()).dt.days
        
        X = daily_fraud['days_since_start'].values
        y = daily_fraud['fraud_rate'].values
        
        # Fit model
        slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
        
        # Generate forecast
        last_day = X[-1]
        future_days = np.arange(last_day + 1, last_day + days_ahead + 1)
        forecast = slope * future_days + intercept
        
        # Clip to [0, 1] range
        forecast = np.clip(forecast, 0, 1)
        
        return {
            'forecast_period_days': days_ahead,
            'model': 'linear_regression',
            'r_squared': float(r_value ** 2),
            'current_rate': float(y[-1]),
            'forecast': [
                {
                    'day': int(day - last_day),
                    'predicted_rate': float(rate)
                }
                for day, rate in zip(future_days, forecast)
            ],
            'avg_forecast_rate': float(np.mean(forecast)),
            'trend': 'increasing' if slope > 0 else 'decreasing'
        }
    
    def plot_fraud_timeline(self, df: pd.DataFrame, 
                           output_name: str = 'fraud_timeline.png'):
        """
        Create timeline visualization
        
        Args:
            df: DataFrame with time-series data
            output_name: Output filename
        
        Returns:
            Path to saved plot
        """
        if df.empty or 'timestamp' not in df.columns:
            print("⚠️  No temporal data to plot")
            return None
        
        print("📊 Creating fraud timeline plot...")
        
        # Calculate daily fraud rate
        daily = self.calculate_fraud_rate_over_time(df, 'D')
        
        # Create plot
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # Plot 1: Fraud counts over time
        axes[0].plot(daily['timestamp'], daily['fraud_count'], 
                    label='Fraud Cases', color='red', linewidth=2)
        axes[0].plot(daily['timestamp'], daily['total_count'], 
                    label='Total Cases', color='blue', linewidth=2, alpha=0.7)
        axes[0].set_title('Fraud Cases Over Time', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Date')
        axes[0].set_ylabel('Number of Cases')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Fraud rate with moving average
        axes[1].plot(daily['timestamp'], daily['fraud_rate'] * 100, 
                    label='Daily Fraud Rate', color='orange', linewidth=1, alpha=0.6)
        
        if len(daily) >= 7:
            ma7 = daily['fraud_rate'].rolling(window=7).mean() * 100
            axes[1].plot(daily['timestamp'], ma7, 
                        label='7-Day Moving Average', color='red', linewidth=2)
        
        axes[1].set_title('Fraud Rate Over Time (%)', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Date')
        axes[1].set_ylabel('Fraud Rate (%)')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save
        output_path = self.output_dir / output_name
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Timeline plot saved: {output_path}")
        
        return str(output_path)
    
    def plot_seasonality(self, df: pd.DataFrame,
                        output_name: str = 'seasonality_patterns.png'):
        """
        Create seasonality visualization
        
        Args:
            df: DataFrame with time-series data
            output_name: Output filename
        
        Returns:
            Path to saved plot
        """
        if df.empty:
            return None
        
        print("📊 Creating seasonality plots...")
        
        fraud_df = df[df['is_fraudulent'] == True]
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        # Plot 1: Day of week
        if 'day_of_week' in fraud_df.columns:
            dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            dow_counts = fraud_df['day_of_week'].value_counts().reindex(dow_order, fill_value=0)
            
            axes[0].bar(range(len(dow_counts)), dow_counts.values, color='steelblue')
            axes[0].set_xticks(range(len(dow_counts)))
            axes[0].set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], rotation=45)
            axes[0].set_title('Fraud by Day of Week')
            axes[0].set_ylabel('Fraud Cases')
            axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Hourly pattern
        if 'hour' in fraud_df.columns:
            hour_counts = fraud_df['hour'].value_counts().sort_index()
            
            axes[1].plot(hour_counts.index, hour_counts.values, marker='o', color='coral', linewidth=2)
            axes[1].set_title('Fraud by Hour of Day')
            axes[1].set_xlabel('Hour')
            axes[1].set_ylabel('Fraud Cases')
            axes[1].set_xticks(range(0, 24, 3))
            axes[1].grid(True, alpha=0.3)
        
        # Plot 3: Monthly pattern
        if 'month' in fraud_df.columns:
            month_counts = fraud_df['month'].value_counts().sort_index()
            
            axes[2].bar(range(len(month_counts)), month_counts.values, color='lightgreen')
            axes[2].set_title('Fraud by Month')
            axes[2].set_xlabel('Month')
            axes[2].set_ylabel('Fraud Cases')
            axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save
        output_path = self.output_dir / output_name
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Seasonality plot saved: {output_path}")
        
        return str(output_path)
    
    def generate_time_series_report(self, data_source: str = 'blockchain/storage') -> Dict:
        """
        Generate comprehensive time-series analysis report
        
        Args:
            data_source: Path to data directory
        
        Returns:
            Time-series analysis report
        """
        print("📈 Generating Time-Series Analysis Report...\n")
        
        # Load data
        df = self.load_time_series_data(data_source)
        
        if df.empty:
            return {'error': 'No time-series data available'}
        
        print(f"✅ Loaded {len(df)} cases with timestamps\n")
        
        # Perform analyses
        trends = self.detect_trends(df)
        seasonality = self.detect_seasonality(df)
        forecast = self.forecast_future_fraud(df, days_ahead=30)
        
        # Generate plots
        timeline_plot = self.plot_fraud_timeline(df)
        seasonality_plot = self.plot_seasonality(df)
        
        # Compile report
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'data_period': {
                'start': str(df['timestamp'].min()),
                'end': str(df['timestamp'].max()),
                'total_days': (df['timestamp'].max() - df['timestamp'].min()).days
            },
            'trend_analysis': trends,
            'seasonality_analysis': seasonality,
            'forecast': forecast,
            'visualizations': {
                'timeline': timeline_plot,
                'seasonality': seasonality_plot
            }
        }
        
        # Save report
        report_path = self.output_dir / 'time_series_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Time-series analysis complete!")
        print(f"📄 Report saved: {report_path}")
        
        return report


# Example usage
if __name__ == "__main__":
    print("📈 LandGuard Time-Series Analysis Demo\n")
    
    # Initialize analyzer
    analyzer = TimeSeriesAnalyzer()
    
    # Generate comprehensive report
    report = analyzer.generate_time_series_report('blockchain/storage')
    
    # Print summary
    print("\n" + "="*70)
    print("📈 TIME-SERIES ANALYSIS SUMMARY")
    print("="*70)
    
    if 'error' not in report:
        trend = report['trend_analysis']
        print(f"\n📊 Trend Analysis:")
        print(f"   Trend: {trend['trend'].upper()}")
        print(f"   {trend['interpretation']}")
        print(f"   Current Rate: {trend['current_rate']:.2%}")
        
        if 'seasonality_analysis' in report:
            seasonality = report['seasonality_analysis']
            if 'day_of_week' in seasonality:
                print(f"\n📅 Seasonality:")
                print(f"   Peak Day: {seasonality['day_of_week']['peak_day']}")
                if 'hourly' in seasonality:
                    print(f"   Peak Hour: {seasonality['hourly']['peak_hour']}:00")
        
        if 'forecast' in report and 'error' not in report['forecast']:
            forecast = report['forecast']
            print(f"\n🔮 30-Day Forecast:")
            print(f"   Avg Predicted Rate: {forecast['avg_forecast_rate']:.2%}")
            print(f"   Trend: {forecast['trend']}")
    
    print("\n" + "="*70)
    print("\n✅ Time-Series Analysis Complete!")