# 📊 Phase 10: Advanced Analytics - Complete Guide

## 📋 Overview

Phase 10 adds powerful analytics capabilities to extract actionable insights from your fraud detection data:

- **Statistical Analysis** - Comprehensive statistics and hypothesis testing
- **Geographic Mapping** - Interactive heatmaps and choropleth maps
- **Network Analysis** - Ownership chains and fraud clusters
- **Time-Series Analysis** - Trends, forecasting, and seasonality
- **Interactive Dashboards** - All-in-one analytics visualization

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              ADVANCED ANALYTICS SYSTEM                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Statistical Analyzer                                     │
│     ├─ Summary statistics (mean, median, std, quartiles)    │
│     ├─ Temporal patterns (hourly, daily, monthly)           │
│     ├─ Outlier detection (Z-score, IQR)                     │
│     ├─ Correlation analysis                                 │
│     └─ Hypothesis testing (T-test, Chi-square)              │
│                           ↓                                   │
│  2. Geographic Mapper                                        │
│     ├─ Fraud heatmaps (Folium)                              │
│     ├─ Cluster maps                                          │
│     ├─ State choropleth                                     │
│     └─ Timeline animations                                   │
│                           ↓                                   │
│  3. Network Analyzer                                        │
│     ├─ Ownership graphs (NetworkX)                          │
│     ├─ Fraud cluster detection                              │
│     ├─ Centrality metrics (degree, betweenness, PageRank)   │
│     ├─ Suspicious pattern detection                         │
│     └─ Interactive network visualization (Pyvis)            │
│                           ↓                                   │
│  4. Time-Series Analyzer                                    │
│     ├─ Trend detection (linear regression)                  │
│     ├─ Seasonality analysis                                 │
│     ├─ Moving averages                                      │
│     ├─ Forecasting (30-day prediction)                      │
│     └─ Matplotlib visualizations                            │
│                           ↓                                   │
│  5. Dashboard Generator                                     │
│     ├─ Comprehensive HTML dashboards                        │
│     ├─ Real-time metrics                                    │
│     ├─ Embedded visualizations                              │
│     └─ Alerts & recommendations                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites

```bash
# Python 3.8+
python --version

# Existing LandGuard (Phases 1-7)
# Blockchain storage (Phase 5) recommended
```

### Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install analytics libraries
pip install pandas==2.0.3
pip install numpy==1.24.3
pip install scipy==1.11.1
pip install matplotlib==3.7.2
pip install seaborn==0.12.2

# Geographic visualization
pip install folium==0.14.0

# Network analysis
pip install networkx==3.1
pip install pyvis==0.3.2

# Already installed from previous phases
# scikit-learn (Phase 7)
# requests (Phase 5)
```

### Verify Installation

```bash
python -c "import pandas; print('✅ pandas')"
python -c "import folium; print('✅ folium')"
python -c "import networkx; print('✅ networkx')"
python -c "import matplotlib; print('✅ matplotlib')"
```

---

## 🚀 Quick Start

### 1. Project Structure

```bash
cd landguard
mkdir -p analytics/outputs/{reports,maps,graphs,dashboards}
```

Add Phase 10 files:

```
landguard/
├── analytics/
│   ├── __init__.py
│   ├── statistical_analyzer.py       # ← Artifact 1
│   ├── geo_mapper.py                 # ← Artifact 2
│   ├── network_analyzer.py           # ← Artifact 3
│   ├── time_series_analyzer.py       # ← Artifact 4
│   └── dashboard_generator.py        # ← Artifact 5
├── analytics/outputs/
│   ├── reports/                      # Statistical reports & charts
│   ├── maps/                         # Geographic visualizations
│   ├── graphs/                       # Network visualizations
│   └── dashboards/                   # HTML dashboards
```

### 2. Run Statistical Analysis

```python
# scripts/run_statistical_analysis.py
from analytics.statistical_analyzer import StatisticalAnalyzer

# Initialize analyzer
analyzer = StatisticalAnalyzer('blockchain/storage')

# Generate comprehensive report
report = analyzer.generate_report(
    'analytics/outputs/reports/statistical_report.json'
)

# Print summary
analyzer.print_summary(report)
```

Run:
```bash
python scripts/run_statistical_analysis.py
```

Expected output:
```
📊 Generating Statistical Analysis Report...

✅ Loaded 150 cases (45 fraud)

======================================================================
📊 STATISTICAL ANALYSIS SUMMARY
======================================================================

📈 Overview:
   Total Cases: 150
   Fraud Cases: 45 (30.0%)
   Normal Cases: 105

📊 Risk Score Statistics:
   Mean: 42.35
   Median: 38.50
   Std Dev: 28.42
   Range: 5.00 - 98.50

⏰ Temporal Patterns:
   Peak Hour: 14:00 (12 cases)

🔍 Outliers Detected:
   Z-Score Method: 8 outliers
   IQR Method: 12 outliers

🔗 Strong Correlations:
   risk_score ↔ fraud_indicators: 0.892
   anomaly_score ↔ classifier_probability: 0.856

======================================================================
```

### 3. Create Geographic Maps

```python
# scripts/create_maps.py
from analytics.geo_mapper import GeoMapper

# Initialize mapper
mapper = GeoMapper()

# Generate all maps
maps = mapper.generate_geo_report('blockchain/storage')

print("\n📁 Generated Maps:")
for map_type, path in maps.items():
    if path:
        print(f"   {map_type}: {path}")
```

Run:
```bash
python scripts/create_maps.py
```

Expected output:
```
🗺️  Generating Geographic Analysis...

✅ Loaded 150 cases with coordinates

🗺️  Creating fraud heatmap...
✅ Heatmap saved: analytics/outputs/maps/fraud_heatmap.html

🗺️  Creating cluster map...
✅ Cluster map saved: analytics/outputs/maps/fraud_clusters.html

🗺️  Creating state choropleth...
✅ State choropleth saved: analytics/outputs/maps/state_fraud_rates.html

🗺️  Creating timeline map...
✅ Timeline map saved: analytics/outputs/maps/fraud_timeline.html

✅ Generated 4 maps
```

### 4. Analyze Networks

```python
# scripts/analyze_networks.py
from analytics.network_analyzer import NetworkAnalyzer

# Initialize analyzer
analyzer = NetworkAnalyzer()

# Generate network analysis
report = analyzer.generate_network_report('blockchain/storage')

# Print summary
print("\n🕸️  NETWORK ANALYSIS SUMMARY")
print("="*70)

stats = report['network_statistics']
print(f"\n📊 Network Statistics:")
print(f"   Total Nodes: {stats['total_nodes']}")
print(f"   Total Edges: {stats['total_edges']}")
print(f"   Fraud Nodes: {stats['fraud_nodes']}")
print(f"   Network Density: {stats['density']:.4f}")

clusters = report['fraud_clusters']
print(f"\n🔍 Fraud Clusters:")
print(f"   Clusters Found: {clusters['num_clusters']}")
if clusters['cluster_sizes']:
    print(f"   Largest Cluster: {max(clusters['cluster_sizes'])} nodes")
```

Run:
```bash
python scripts/analyze_networks.py
```

### 5. Generate Complete Dashboard

```python
# scripts/generate_dashboard.py
from analytics.dashboard_generator import DashboardGenerator

# Initialize generator
generator = DashboardGenerator()

# Generate comprehensive dashboard
dashboard_path = generator.generate_html_dashboard('blockchain/storage')

print(f"\n✅ Dashboard generated: {dashboard_path}")
print("💡 Open this file in your web browser!")
```

Run:
```bash
python scripts/generate_dashboard.py
```

Expected output:
```
🎨 Generating Analytics Dashboard...

1️⃣  Running statistical analysis...
✅ Loaded 150 cases (45 fraud)

2️⃣  Running geographic analysis...
✅ Loaded 150 cases with coordinates
✅ Generated 4 maps

3️⃣  Running network analysis...
✅ Network built:
   Nodes: 450
   Edges: 300
   Fraud nodes: 135

4️⃣  Running time-series analysis...
✅ Loaded 150 cases with timestamps

✅ Dashboard generated: analytics/outputs/dashboards/analytics_dashboard.html
```

---

## 📊 Features Deep Dive

### 1. Statistical Analysis

**Capabilities:**
- Summary statistics (mean, median, std, quartiles)
- Fraud rate analysis
- Outlier detection (Z-score & IQR methods)
- Correlation analysis
- Hypothesis testing (T-test, Chi-square)
- Temporal pattern analysis

**Example Output:**
```json
{
  "summary_statistics": {
    "overview": {
      "total_cases": 150,
      "fraud_cases": 45,
      "fraud_rate": 0.30
    },
    "risk_scores": {
      "mean": 42.35,
      "median": 38.50,
      "std": 28.42,
      "quartiles": {
        "q1": 15.25,
        "q2": 38.50,
        "q3": 67.75
      }
    }
  },
  "outlier_analysis": {
    "z_score_method": {
      "num_outliers": 8,
      "threshold": 3.0
    },
    "iqr_method": {
      "num_outliers": 12,
      "lower_bound": -62.5,
      "upper_bound": 145.5
    }
  }
}
```

**Usage:**
```python
from analytics.statistical_analyzer import StatisticalAnalyzer

analyzer = StatisticalAnalyzer()

# Load data
df = analyzer.load_fraud_cases()

# Compute statistics
stats = analyzer.compute_summary_statistics(df)

# Detect outliers
outliers = analyzer.detect_outliers(df, column='risk_score')

# Analyze correlations
correlations = analyzer.analyze_correlations(df)

# Hypothesis tests
tests = analyzer.perform_hypothesis_tests(df)
```

---

### 2. Geographic Mapping

**Capabilities:**
- Interactive fraud heatmaps
- Clustered marker maps
- State/region choropleth
- Timeline animations
- Custom markers with popups

**Map Types:**

**A. Fraud Heatmap**
```python
mapper = GeoMapper()
df = mapper.load_geo_data()
mapper.create_fraud_heatmap(df, 'fraud_heatmap.html')
```

Features:
- Gradient coloring (blue → yellow → orange → red)
- Intensity based on risk score
- Interactive zoom/pan

**B. Cluster Map**
```python
mapper.create_cluster_map(df, 'fraud_clusters.html')
```

Features:
- Marker clustering for performance
- Color-coded by fraud status
- Popup with case details
- Legend

**C. State Choropleth**
```python
mapper.create_state_choropleth(df, 'state_rates.html')
```

Features:
- Fraud rate by geographic region
- Circle markers sized by rate
- State statistics

**Interactive Features:**
- Click markers for details
- Zoom to area of interest
- Layer controls
- Search functionality

---

### 3. Network Analysis

**Capabilities:**
- Build ownership graphs
- Detect fraud clusters
- Calculate centrality metrics
- Identify suspicious patterns
- Interactive visualization

**Network Metrics:**

**A. Degree Centrality**
```python
analyzer = NetworkAnalyzer()
analyzer.build_ownership_network()
metrics = analyzer.calculate_centrality_metrics()

# Top nodes by connections
degree = metrics['degree_centrality']['top_nodes']
# [{'node': 'Owner_42', 'score': 0.156}, ...]
```

**B. Betweenness Centrality**
- Identifies "bridge" nodes
- Key players connecting fraud networks

**C. PageRank**
- Most influential nodes
- Weighted by connection importance

**Fraud Pattern Detection:**

**1. Circular Ownership**
```python
patterns = analyzer.detect_suspicious_patterns()
circular = patterns['circular_ownership']
# [[Owner_A → Property → Owner_B → Property → Owner_A], ...]
```

**2. High-Risk Connections**
```python
high_risk = patterns['high_risk_connections']
# Nodes with multiple fraud connections
```

**3. Isolated Fraud**
```python
isolated = patterns['isolated_fraud']
# Fraud cases with no connections to other fraud
```

**Visualization:**
```python
# Full network
analyzer.visualize_network('network.html', max_nodes=100)

# Specific cluster
cluster = analyzer.find_fraud_clusters()[0]
analyzer.visualize_fraud_cluster(cluster, 'cluster.html')
```

---

### 4. Time-Series Analysis

**Capabilities:**
- Trend detection
- Seasonality analysis
- Moving averages
- Forecasting
- Visualization

**A. Trend Detection**
```python
ts_analyzer = TimeSeriesAnalyzer()
df = ts_analyzer.load_time_series_data()

trends = ts_analyzer.detect_trends(df)
# {
#   'trend': 'increasing',
#   'slope': 0.0023,
#   'r_squared': 0.78,
#   'p_value': 0.003,
#   'interpretation': 'Fraud rate is significantly increasing'
# }
```

**B. Seasonality Detection**
```python
seasonality = ts_analyzer.detect_seasonality(df)
# {
#   'day_of_week': {
#     'peak_day': 'Friday',
#     'peak_count': 15
#   },
#   'hourly': {
#     'peak_hour': 14,
#     'peak_count': 8
#   }
# }
```

**C. Forecasting**
```python
forecast = ts_analyzer.forecast_future_fraud(df, days_ahead=30)
# {
#   'avg_forecast_rate': 0.32,
#   'trend': 'increasing',
#   'forecast': [
#     {'day': 1, 'predicted_rate': 0.31},
#     {'day': 2, 'predicted_rate': 0.31},
#     ...
#   ]
# }
```

**Visualizations:**
```python
# Timeline plot
ts_analyzer.plot_fraud_timeline(df, 'timeline.png')

# Seasonality patterns
ts_analyzer.plot_seasonality(df, 'seasonality.png')
```

---

### 5. Interactive Dashboard

**Components:**

**A. Key Metrics Cards**
- Total cases analyzed
- Fraud detected (count & percentage)
- Average risk score
- Current trend direction

**B. Statistical Summary**
- Risk score distribution
- Outlier counts
- Correlation highlights

**C. Geographic Section**
- Links to all generated maps
- Embedded map previews

**D. Network Section**
- Network statistics
- Cluster information
- Link to interactive network graph

**E. Time-Series Section**
- Trend analysis
- 30-day forecast
- Links to charts

**F. Alerts & Recommendations**
- High fraud rate warnings
- Increasing trend alerts
- Cluster detection notices

**Dashboard Features:**
- Responsive design
- Color-coded metrics
- Interactive elements
- Real-time updates

---

## 🎯 Use Cases

### Use Case 1: Monthly Fraud Report

```python
from analytics.dashboard_generator import DashboardGenerator

# Generate monthly report
generator = DashboardGenerator()
dashboard = generator.generate_html_dashboard(
    data_source='blockchain/storage',
    output_name=f'monthly_report_{datetime.now().strftime("%Y_%m")}.html'
)

# Email to stakeholders
# send_email(to='management@company.com', attachment=dashboard)
```

### Use Case 2: Geographic Fraud Investigation

```python
from analytics.geo_mapper import GeoMapper

mapper = GeoMapper()
df = mapper.load_geo_data()

# Create focused heatmap for high-fraud region
high_fraud_df = df[df['risk_score'] > 70]
mapper.create_fraud_heatmap(high_fraud_df, 'high_risk_areas.html')

# Investigate clusters
mapper.create_cluster_map(high_fraud_df, 'investigation_map.html')
```

### Use Case 3: Network Fraud Ring Detection

```python
from analytics.network_analyzer import NetworkAnalyzer

analyzer = NetworkAnalyzer()
analyzer.build_ownership_network()

# Find fraud clusters
clusters = analyzer.find_fraud_clusters()

for i, cluster in enumerate(clusters):
    if len(cluster) > 5:  # Significant cluster
        print(f"Suspected fraud ring detected: {len(cluster)} connected cases")
        
        # Visualize for investigation
        analyzer.visualize_fraud_cluster(
            cluster, 
            f'fraud_ring_{i}.html'
        )
```

### Use Case 4: Predictive Analysis

```python
from analytics.time_series_analyzer import TimeSeriesAnalyzer

analyzer = TimeSeriesAnalyzer()
df = analyzer.load_time_series_data()

# Detect trend
trends = analyzer.detect_trends(df)

if trends['trend'] == 'increasing':
    # Forecast next month
    forecast = analyzer.forecast_future_fraud(df, days_ahead=30)
    
    print(f"⚠️ Warning: Fraud rate increasing!")
    print(f"Current: {trends['current_rate']:.2%}")
    print(f"Predicted (30 days): {forecast['avg_forecast_rate']:.2%}")
    
    # Alert management
    # send_alert("Fraud rate predicted to increase by 15%")
```

### Use Case 5: Performance Benchmarking

```python
from analytics.statistical_analyzer import StatisticalAnalyzer

analyzer = StatisticalAnalyzer()
df = analyzer.load_fraud_cases()

# Compare periods
q1 = df[df['timestamp'].dt.quarter == 1]
q2 = df[df['timestamp'].dt.quarter == 2]

q1_rate = q1['is_fraudulent'].mean()
q2_rate = q2['is_fraudulent'].mean()

improvement = ((q1_rate - q2_rate) / q1_rate) * 100

print(f"Q1 Fraud Rate: {q1_rate:.2%}")
print(f"Q2 Fraud Rate: {q2_rate:.2%}")
print(f"Improvement: {improvement:.1f}%")
```

---

## 📈 Integration Examples

### With Phase 5 (Blockchain)

```python
from blockchain.audit_trail import AuditTrail
from analytics.statistical_analyzer import StatisticalAnalyzer

# Analyze audit trail
audit = AuditTrail()
history = audit.get_events(limit=1000)

# Convert to DataFrame
df = pd.DataFrame(history)

# Analyze event patterns
analyzer = StatisticalAnalyzer()
event_stats = df['event_type'].value_counts()

print("Most common events:")
print(event_stats)
```

### With Phase 7 (ML)

```python
from ml.ml_pipeline import MLFraudDetectionPipeline
from analytics.time_series_analyzer import TimeSeriesAnalyzer

# Compare ML performance over time
ml_pipeline = MLFraudDetectionPipeline()
ts_analyzer = TimeSeriesAnalyzer()

df = ts_analyzer.load_time_series_data()

# Add ML accuracy column
df['ml_correct'] = df['ml_prediction'] == df['actual_fraud']

# Analyze accuracy trend
accuracy_trend = df.groupby('date')['ml_correct'].mean()

print(f"ML Accuracy Trend:")
print(f"Start: {accuracy_trend.iloc[0]:.2%}")
print(f"End: {accuracy_trend.iloc[-1]:.2%}")
```

---

## 🧪 Testing

### Unit Tests

```python
# tests/test_analytics.py
import pytest
from analytics.statistical_analyzer import StatisticalAnalyzer
from analytics.network_analyzer import NetworkAnalyzer
import pandas as pd
import numpy as np

def test_statistical_analysis():
    """Test statistical calculations"""
    analyzer = StatisticalAnalyzer()
    
    # Create test data
    df = pd.DataFrame({
        'risk_score': np.random.normal(50, 20, 100),
        'is_fraudulent': np.random.choice([True, False], 100)
    })
    
    stats = analyzer.compute_summary_statistics(df)
    
    assert 'overview' in stats
    assert 'risk_scores' in stats
    assert stats['overview']['total_cases'] == 100

def test_outlier_detection():
    """Test outlier detection"""
    analyzer = StatisticalAnalyzer()
    
    # Data with known outliers
    df = pd.DataFrame({
        'risk_score': [10, 12, 11, 13, 100, 11, 12, 10]  # 100 is outlier
    })
    
    outliers = analyzer.detect_outliers(df, 'risk_score')
    
    assert outliers['z_score_method']['num_outliers'] > 0

def test_network_building():
    """Test network construction"""
    analyzer = NetworkAnalyzer()
    analyzer.build_ownership_network('blockchain/storage')
    
    assert analyzer.graph.number_of_nodes() > 0
    assert analyzer.graph.number_of_edges() > 0

def test_fraud_cluster_detection():
    """Test cluster detection"""
    analyzer = NetworkAnalyzer()
    analyzer.build_ownership_network('blockchain/storage')
    
    clusters = analyzer.find_fraud_clusters()
    
    assert isinstance(clusters, list)
```

Run tests:
```bash
pytest tests/test_analytics.py -v
```

---

## 🚧 Troubleshooting

### Issue: No data in analytics

**Cause:** No fraud cases stored in blockchain/storage

**Solution:**
```python
# Check if evidence exists
from pathlib import Path

evidence_dir = Path('blockchain/storage/evidence')
files = list(evidence_dir.glob('*_complete.json'))

print(f"Found {len(files)} evidence files")

# If empty, run some analyses first (Phase 7 ML or Phase 1 Analyzer)
```

### Issue: Maps not displaying

**Cause:** JavaScript blocked or incorrect file paths

**Solution:**
- Open HTML files in browser (don't just view source)
- Check browser console for errors
- Ensure all map files are in `analytics/outputs/maps/`

### Issue: "matplotlib backend" error

**Cause:** Display backend not available

**Solution:**
```python
# Add to top of script
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
```

### Issue: Network visualization too slow

**Cause:** Too many nodes

**Solution:**
```python
# Limit nodes for performance
analyzer.visualize_network('network.html', max_nodes=50)

# Or sample most important nodes
```

---

## 📊 Performance Tips

### Large Datasets

```python
# Process in chunks
chunk_size = 1000

for chunk in pd.read_json('large_data.json', chunksize=chunk_size):
    # Analyze chunk
    stats = analyzer.compute_summary_statistics(chunk)
```

### Caching Results

```python
import pickle

# Cache expensive computations
cache_file = 'analytics_cache.pkl'

if Path(cache_file).exists():
    with open(cache_file, 'rb') as f:
        results = pickle.load(f)
else:
    # Run analysis
    results = analyzer.generate_report()
    
    # Cache for next time
    with open(cache_file, 'wb') as f:
        pickle.dump(results, f)
```

---

## 🎉 Success Metrics

After implementing Phase 10, you should have:

✅ **Comprehensive statistical insights** into fraud patterns
✅ **Interactive geographic visualizations** of fraud hotspots
✅ **Network analysis** revealing fraud rings and relationships
✅ **Time-series forecasting** to predict future trends
✅ **Beautiful dashboards** for stakeholder presentations

---

## 🔮 Future Enhancements

1. **Real-time Streaming Analytics**
   - Live dashboard updates
   - WebSocket connections
   - Real-time alerts

2. **Advanced ML Integration**
   - Automated pattern discovery
   - Clustering algorithms
   - Classification improvements

3. **Export Capabilities**
   - Excel reports
   - PowerPoint presentations
   - PDF exports

4. **API Endpoints**
   - REST API for analytics
   - Query parameters
   - Data filters

---

## ✅ Phase 10 Complete!

Your LandGuard system now has:
- Deep statistical insights
- Geographic fraud mapping
- Network relationship analysis
- Temporal trend analysis
- Beautiful interactive dashboards

**Remaining Phases for Member B:**
- ✅ Phase 7: ML Enhancement (Complete)
- ✅ Phase 5: Blockchain (Complete)
- ✅ Phase 10: Analytics (Complete)
- 📋 Phase 4: Advanced Reporting
- 📋 Phase 11: Integrations

**Which phase next?** All analytics complete! 🎊