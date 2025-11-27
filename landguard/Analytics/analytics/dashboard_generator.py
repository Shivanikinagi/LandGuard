"""
LandGuard Analytics Dashboard Generator
Create comprehensive interactive dashboards combining all analytics
"""

from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any

from statistical_analyzer import StatisticalAnalyzer
from geo_mapper import GeoMapper
from network_analyzer import NetworkAnalyzer
from time_series_analyzer import TimeSeriesAnalyzer


class DashboardGenerator:
    """Generate comprehensive analytics dashboards"""
    
    def __init__(self, output_dir: str = 'analytics/outputs/dashboards'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize all analyzers
        self.stats_analyzer = StatisticalAnalyzer()
        self.geo_mapper = GeoMapper()
        self.network_analyzer = NetworkAnalyzer()
        self.time_series_analyzer = TimeSeriesAnalyzer()
    
    def generate_html_dashboard(self, 
                                data_source: str = 'blockchain/storage',
                                output_name: str = 'analytics_dashboard.html') -> str:
        """
        Generate comprehensive HTML dashboard
        
        Args:
            data_source: Path to data directory
            output_name: Output filename
        
        Returns:
            Path to generated dashboard
        """
        print("🎨 Generating Analytics Dashboard...\n")
        
        # Run all analyses
        print("1️⃣  Running statistical analysis...")
        stats_report = self.stats_analyzer.generate_report()
        
        print("\n2️⃣  Running geographic analysis...")
        geo_maps = self.geo_mapper.generate_geo_report(data_source)
        
        print("\n3️⃣  Running network analysis...")
        network_report = self.network_analyzer.generate_network_report(data_source)
        
        print("\n4️⃣  Running time-series analysis...")
        time_report = self.time_series_analyzer.generate_time_series_report(data_source)
        
        # Generate HTML
        html = self._create_html_template(
            stats_report, geo_maps, network_report, time_report
        )
        
        # Save dashboard
        output_path = self.output_dir / output_name
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ Dashboard generated: {output_path}")
        
        return str(output_path)
    
    def _create_html_template(self, stats: Dict, geo: Dict, 
                             network: Dict, timeseries: Dict) -> str:
        """Create HTML dashboard template"""
        
        # Extract key metrics
        overview = stats.get('summary_statistics', {}).get('overview', {})
        risk_scores = stats.get('summary_statistics', {}).get('risk_scores', {})
        trend = timeseries.get('trend_analysis', {})
        network_stats = network.get('network_statistics', {})
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LandGuard Analytics Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}
        
        .dashboard {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #666;
        }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-card h3 {{
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        
        .metric-value {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .metric-label {{
            color: #999;
            font-size: 14px;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        .stat-row {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        
        .stat-label {{
            color: #666;
        }}
        
        .stat-value {{
            font-weight: bold;
            color: #333;
        }}
        
        .trend-up {{
            color: #e74c3c;
        }}
        
        .trend-down {{
            color: #27ae60;
        }}
        
        .trend-stable {{
            color: #f39c12;
        }}
        
        .map-container {{
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .link-button {{
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 5px;
            transition: background 0.3s ease;
        }}
        
        .link-button:hover {{
            background: #5568d3;
        }}
        
        .alert {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }}
        
        .alert.danger {{
            background: #f8d7da;
            border-left-color: #dc3545;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <!-- Header -->
        <div class="header">
            <h1>🛡️ LandGuard Analytics Dashboard</h1>
            <p>Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
        </div>
        
        <!-- Key Metrics -->
        <div class="metrics">
            <div class="metric-card">
                <h3>Total Cases Analyzed</h3>
                <div class="metric-value">{overview.get('total_cases', 0)}</div>
                <div class="metric-label">All Records</div>
            </div>
            
            <div class="metric-card">
                <h3>Fraud Detected</h3>
                <div class="metric-value" style="color: #e74c3c;">{overview.get('fraud_cases', 0)}</div>
                <div class="metric-label">{overview.get('fraud_rate', 0)*100:.1f}% of total</div>
            </div>
            
            <div class="metric-card">
                <h3>Average Risk Score</h3>
                <div class="metric-value">{risk_scores.get('mean', 0):.1f}</div>
                <div class="metric-label">out of 100</div>
            </div>
            
            <div class="metric-card">
                <h3>Fraud Trend</h3>
                <div class="metric-value trend-{trend.get('trend', 'stable')}">{trend.get('trend', 'Unknown').upper()}</div>
                <div class="metric-label">{trend.get('interpretation', 'N/A')[:50]}...</div>
            </div>
        </div>
        
        <!-- Statistical Summary -->
        <div class="section">
            <h2>📊 Statistical Summary</h2>
            
            <div class="stat-row">
                <span class="stat-label">Median Risk Score</span>
                <span class="stat-value">{risk_scores.get('median', 0):.2f}</span>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">Standard Deviation</span>
                <span class="stat-value">{risk_scores.get('std', 0):.2f}</span>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">Risk Score Range</span>
                <span class="stat-value">{risk_scores.get('min', 0):.1f} - {risk_scores.get('max', 0):.1f}</span>
            </div>
            
            {self._generate_outlier_section(stats)}
        </div>
        
        <!-- Geographic Analysis -->
        <div class="section">
            <h2>🗺️ Geographic Analysis</h2>
            <p>Interactive maps showing fraud distribution and hotspots.</p>
            
            <div class="map-container">
                {self._generate_map_links(geo)}
            </div>
        </div>
        
        <!-- Network Analysis -->
        <div class="section">
            <h2>🕸️ Network Analysis</h2>
            
            <div class="stat-row">
                <span class="stat-label">Total Network Nodes</span>
                <span class="stat-value">{network_stats.get('total_nodes', 0)}</span>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">Fraud Nodes</span>
                <span class="stat-value">{network_stats.get('fraud_nodes', 0)}</span>
            </div>
            
            <div class="stat-row">
                <span class="stat-label">Network Density</span>
                <span class="stat-value">{network_stats.get('density', 0):.4f}</span>
            </div>
            
            {self._generate_cluster_info(network)}
            
            <div style="margin-top: 20px;">
                <a href="../graphs/ownership_network.html" class="link-button" target="_blank">
                    View Network Visualization
                </a>
            </div>
        </div>
        
        <!-- Time-Series Analysis -->
        <div class="section">
            <h2>📈 Time-Series Analysis</h2>
            
            {self._generate_trend_section(timeseries)}
            {self._generate_forecast_section(timeseries)}
            
            <div style="margin-top: 20px;">
                <a href="../reports/fraud_timeline.png" class="link-button" target="_blank">
                    View Timeline Chart
                </a>
                <a href="../reports/seasonality_patterns.png" class="link-button" target="_blank">
                    View Seasonality Patterns
                </a>
            </div>
        </div>
        
        <!-- Alerts & Recommendations -->
        <div class="section">
            <h2>⚠️ Alerts & Recommendations</h2>
            
            {self._generate_alerts(stats, network, timeseries)}
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>🛡️ LandGuard Analytics System | Powered by Advanced ML & Blockchain</p>
            <p style="font-size: 12px; margin-top: 10px;">
                All data is cryptographically secured and stored on IPFS
            </p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_map_links(self, geo: Dict) -> str:
        """Generate links to geographic maps"""
        html = ""
        
        map_types = {
            'heatmap': '🔥 Fraud Heatmap',
            'clusters': '📍 Cluster Map',
            'states': '🗺️ State Analysis',
            'timeline': '⏰ Timeline Map'
        }
        
        for key, label in map_types.items():
            if key in geo and geo[key]:
                html += f'<a href="../maps/{Path(geo[key]).name}" class="link-button" target="_blank">{label}</a>\n'
        
        return html or "<p>No geographic maps generated</p>"
    
    def _generate_outlier_section(self, stats: Dict) -> str:
        """Generate outlier detection section"""
        outliers = stats.get('outlier_analysis', {})
        
        if 'z_score_method' not in outliers:
            return ""
        
        z_outliers = outliers['z_score_method']['num_outliers']
        iqr_outliers = outliers['iqr_method']['num_outliers']
        
        return f"""
        <div style="margin-top: 20px;">
            <h3 style="color: #667eea; margin-bottom: 10px;">🔍 Outlier Detection</h3>
            <div class="stat-row">
                <span class="stat-label">Z-Score Outliers</span>
                <span class="stat-value">{z_outliers}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">IQR Outliers</span>
                <span class="stat-value">{iqr_outliers}</span>
            </div>
        </div>
        """
    
    def _generate_cluster_info(self, network: Dict) -> str:
        """Generate fraud cluster information"""
        clusters = network.get('fraud_clusters', {})
        
        if not clusters.get('num_clusters'):
            return ""
        
        return f"""
        <div style="margin-top: 20px;">
            <h3 style="color: #667eea; margin-bottom: 10px;">🔗 Fraud Clusters</h3>
            <div class="stat-row">
                <span class="stat-label">Clusters Detected</span>
                <span class="stat-value">{clusters['num_clusters']}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Largest Cluster</span>
                <span class="stat-value">{max(clusters.get('cluster_sizes', [0]))} nodes</span>
            </div>
        </div>
        """
    
    def _generate_trend_section(self, timeseries: Dict) -> str:
        """Generate trend analysis section"""
        trend = timeseries.get('trend_analysis', {})
        
        if 'error' in trend:
            return "<p>Insufficient data for trend analysis</p>"
        
        trend_class = f"trend-{trend.get('trend', 'stable')}"
        
        return f"""
        <div class="stat-row">
            <span class="stat-label">Trend Direction</span>
            <span class="stat-value {trend_class}">{trend.get('trend', 'Unknown').upper()}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Current Fraud Rate</span>
            <span class="stat-value">{trend.get('current_rate', 0)*100:.2f}%</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">R² Score</span>
            <span class="stat-value">{trend.get('r_squared', 0):.4f}</span>
        </div>
        """
    
    def _generate_forecast_section(self, timeseries: Dict) -> str:
        """Generate forecast section"""
        forecast = timeseries.get('forecast', {})
        
        if 'error' in forecast:
            return ""
        
        return f"""
        <div style="margin-top: 20px;">
            <h3 style="color: #667eea; margin-bottom: 10px;">🔮 30-Day Forecast</h3>
            <div class="stat-row">
                <span class="stat-label">Predicted Avg Rate</span>
                <span class="stat-value">{forecast.get('avg_forecast_rate', 0)*100:.2f}%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Forecast Trend</span>
                <span class="stat-value">{forecast.get('trend', 'Unknown').upper()}</span>
            </div>
        </div>
        """
    
    def _generate_alerts(self, stats: Dict, network: Dict, timeseries: Dict) -> str:
        """Generate alerts based on analysis"""
        alerts = []
        
        # Check fraud rate
        overview = stats.get('summary_statistics', {}).get('overview', {})
        fraud_rate = overview.get('fraud_rate', 0)
        
        if fraud_rate > 0.3:
            alerts.append(('danger', f'⚠️ High fraud rate detected: {fraud_rate*100:.1f}%'))
        
        # Check trend
        trend = timeseries.get('trend_analysis', {})
        if trend.get('trend') == 'increasing':
            alerts.append(('danger', '📈 Fraud cases are increasing over time'))
        
        # Check clusters
        clusters = network.get('fraud_clusters', {})
        if clusters.get('num_clusters', 0) > 3:
            alerts.append(('danger', f'🕸️ Multiple fraud clusters detected ({clusters["num_clusters"]}'))
        
        # Generate HTML
        html = ""
        for alert_type, message in alerts:
            html += f'<div class="alert {alert_type}">{message}</div>\n'
        
        if not alerts:
            html = '<div class="alert">✅ No critical alerts. System operating normally.</div>'
        
        return html


# Example usage
if __name__ == "__main__":
    print("🎨 LandGuard Dashboard Generator Demo\n")
    
    # Initialize generator
    generator = DashboardGenerator()
    
    # Generate comprehensive dashboard
    dashboard_path = generator.generate_html_dashboard('blockchain/storage')
    
    print(f"\n{'='*70}")
    print("🎉 Dashboard Generation Complete!")
    print(f"{'='*70}")
    print(f"\n📁 Dashboard Location: {dashboard_path}")
    print("\n💡 Open this file in your web browser to view the analytics dashboard")
    print("\n✅ All analytics complete!")