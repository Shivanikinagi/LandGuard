"""
LandGuard Phase 4: HTML Report Exporter
Generates beautiful HTML reports with charts
"""

from typing import Dict, Any, List
from datetime import datetime
import json
import logging


logger = logging.getLogger(__name__)


class HTMLExporter:
    """
    Export reports to HTML format with embedded visualizations
    """
    
    def __init__(self):
        self.template_cache = {}
    
    def export(self, report) -> str:
        """
        Export report to HTML
        
        Args:
            report: Report object to export
        
        Returns:
            HTML string
        """
        report_type = report.report_type.value
        
        if report_type == 'fraud_analysis':
            return self._generate_fraud_analysis_html(report)
        elif report_type == 'executive_summary':
            return self._generate_executive_summary_html(report)
        else:
            return self._generate_generic_html(report)
    
    def _generate_fraud_analysis_html(self, report) -> str:
        """Generate HTML for fraud analysis report"""
        
        data = report.to_dict()
        risk_level = data.get('risk_level', 'none')
        risk_colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745',
            'none': '#6c757d'
        }
        risk_color = risk_colors.get(risk_level, '#6c757d')
        
        # Generate findings HTML
        findings_html = self._generate_findings_html(data['findings'])
        
        # Generate recommendations HTML
        recommendations_html = self._generate_recommendations_html(data['recommendations'])
        
        # Generate charts data
        charts_data = self._generate_charts_data(data)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['title']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f7fa;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 14px;
        }}
        
        .report-meta {{
            display: flex;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .meta-item {{
            background: rgba(255,255,255,0.2);
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 14px;
        }}
        
        .risk-badge {{
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 16px;
            text-transform: uppercase;
            background: {risk_color};
            color: white;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 22px;
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        .property-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .property-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .property-card h4 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 14px;
            text-transform: uppercase;
        }}
        
        .property-card p {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }}
        
        .finding {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }}
        
        .finding.critical {{
            background: #f8d7da;
            border-left-color: #dc3545;
        }}
        
        .finding.high {{
            background: #ffe5d0;
            border-left-color: #fd7e14;
        }}
        
        .finding h4 {{
            color: #333;
            margin-bottom: 8px;
            font-size: 16px;
        }}
        
        .finding p {{
            color: #666;
            font-size: 14px;
        }}
        
        .recommendations {{
            background: #d1ecf1;
            border-radius: 8px;
            padding: 20px;
        }}
        
        .recommendations ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .recommendations li {{
            padding: 12px;
            margin-bottom: 10px;
            background: white;
            border-radius: 5px;
            border-left: 4px solid #17a2b8;
        }}
        
        .recommendations li:before {{
            content: "✓ ";
            color: #17a2b8;
            font-weight: bold;
            margin-right: 10px;
        }}
        
        .chart-container {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #666;
            font-size: 14px;
            border-top: 1px solid #dee2e6;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{data['title']}</h1>
            <p>{data.get('description', '')}</p>
            
            <div class="report-meta">
                <div class="meta-item">
                    <strong>Report ID:</strong> {data['report_id']}
                </div>
                <div class="meta-item">
                    <strong>Generated:</strong> {datetime.fromisoformat(data['created_at']).strftime('%Y-%m-%d %H:%M:%S UTC')}
                </div>
                <div class="meta-item">
                    <strong>Property ID:</strong> {data['metadata'].get('property_id', 'N/A')}
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <span class="risk-badge">{risk_level.upper()} RISK</span>
            </div>
        </div>
        
        <div class="content">
            <!-- Property Information -->
            <div class="section">
                <h2 class="section-title">Property Information</h2>
                <div class="property-grid">
                    {self._generate_property_cards(data.get('data', {}).get('property', {}))}
                </div>
            </div>
            
            <!-- Findings -->
            <div class="section">
                <h2 class="section-title">Fraud Detection Findings ({len(data['findings'])})</h2>
                {findings_html}
            </div>
            
            <!-- Recommendations -->
            {recommendations_html}
            
            <!-- Charts -->
            <div class="section">
                <h2 class="section-title">Visual Analysis</h2>
                <div class="chart-container">
                    <p style="text-align: center; color: #666;">
                        📊 Charts would be rendered here using Chart.js or similar library
                    </p>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by LandGuard Fraud Detection System v1.0</p>
            <p>This report is confidential and should be handled according to data protection policies.</p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_property_cards(self, property_data: Dict) -> str:
        """Generate property information cards"""
        if not property_data:
            return '<div class="property-card"><p>No property data available</p></div>'
        
        cards = []
        card_mappings = {
            'survey_number': 'Survey Number',
            'owner_name': 'Owner Name',
            'area': 'Area (sqft)',
            'location': 'Location',
            'property_type': 'Property Type',
            'registration_date': 'Registration Date',
            'market_value': 'Market Value'
        }
        
        for key, label in card_mappings.items():
            if key in property_data:
                value = property_data[key]
                if key == 'market_value' and isinstance(value, (int, float)):
                    value = f"₹{value:,}"
                
                cards.append(f"""
                <div class="property-card">
                    <h4>{label}</h4>
                    <p>{value}</p>
                </div>
                """)
        
        return '\n'.join(cards)
    
    def _generate_findings_html(self, findings: List[Dict]) -> str:
        """Generate HTML for findings"""
        if not findings:
            return '<p style="color: #28a745;">✅ No fraud indicators detected</p>'
        
        findings_html = []
        for finding in findings:
            severity = finding.get('severity', 'medium')
            findings_html.append(f"""
            <div class="finding {severity}">
                <h4>{finding['title']}</h4>
                <p>{finding['description']}</p>
                <small style="color: #999;">Severity: {severity.upper()}</small>
            </div>
            """)
        
        return '\n'.join(findings_html)
    
    def _generate_recommendations_html(self, recommendations: List[str]) -> str:
        """Generate HTML for recommendations"""
        if not recommendations:
            return ''
        
        rec_items = '\n'.join([f'<li>{rec}</li>' for rec in recommendations])
        
        return f"""
        <div class="section">
            <h2 class="section-title">Recommendations ({len(recommendations)})</h2>
            <div class="recommendations">
                <ul>
                    {rec_items}
                </ul>
            </div>
        </div>
        """
    
    def _generate_charts_data(self, data: Dict) -> str:
        """Generate data for charts (JSON format)"""
        # This would generate data for Chart.js or similar
        charts_data = {
            'fraud_types': {},
            'risk_timeline': []
        }
        
        return json.dumps(charts_data)
    
    def _generate_executive_summary_html(self, report) -> str:
        """Generate HTML for executive summary"""
        data = report.to_dict()
        report_data = data.get('data', {})
        
        total = report_data.get('total_properties', 0)
        fraud_detected = report_data.get('fraud_detected', 0)
        fraud_rate = report_data.get('fraud_rate', 0)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['title']}</title>
    <style>
        /* Similar styling as fraud analysis */
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        .stat-card {{
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 10px;
            border-top: 4px solid #667eea;
        }}
        .stat-value {{
            font-size: 48px;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 10px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{data['title']}</h1>
            <p>{data.get('description', '')}</p>
        </div>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{total}</div>
                <div class="stat-label">Total Properties Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #dc3545;">{fraud_detected}</div>
                <div class="stat-label">Fraud Cases Detected</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #ffc107;">{fraud_rate:.1f}%</div>
                <div class="stat-label">Fraud Rate</div>
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_generic_html(self, report) -> str:
        """Generate generic HTML report"""
        data = report.to_dict()
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{data['title']}</title>
</head>
<body>
    <h1>{data['title']}</h1>
    <pre>{json.dumps(data, indent=2)}</pre>
</body>
</html>
"""


# Export
__all__ = ['HTMLExporter']