"""
LandGuard Phase 4: CSV Exporter
Exports report data to CSV format
"""

import csv
from io import StringIO
from typing import Dict, Any, List
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class CSVExporter:
    """
    Export reports to CSV format
    """
    
    def export(self, report) -> str:
        """
        Export report to CSV
        
        Args:
            report: Report object to export
        
        Returns:
            CSV string
        """
        report_type = report.report_type.value
        
        if report_type == 'fraud_analysis':
            return self._export_fraud_analysis(report)
        elif report_type == 'executive_summary':
            return self._export_executive_summary(report)
        else:
            return self._export_generic(report)
    
    def _export_fraud_analysis(self, report) -> str:
        """Export fraud analysis to CSV"""
        output = StringIO()
        
        # Write header information
        output.write("# LandGuard Fraud Analysis Report\n")
        output.write(f"# Report ID: {report.report_id}\n")
        output.write(f"# Generated: {report.created_at.isoformat()}\n")
        output.write(f"# Property ID: {report.metadata.get('property_id', 'N/A')}\n")
        output.write(f"# Risk Level: {report.risk_level.value if report.risk_level else 'N/A'}\n")
        output.write("\n")
        
        # Write property information
        output.write("## Property Information\n")
        property_data = report.data.get('property', {})
        if property_data:
            writer = csv.writer(output)
            writer.writerow(['Field', 'Value'])
            for key, value in property_data.items():
                writer.writerow([key, value])
            output.write("\n")
        
        # Write findings
        output.write("## Fraud Detection Findings\n")
        if report.findings:
            writer = csv.writer(output)
            writer.writerow(['Title', 'Severity', 'Description', 'Timestamp'])
            for finding in report.findings:
                writer.writerow([
                    finding['title'],
                    finding['severity'],
                    finding['description'],
                    finding['timestamp']
                ])
            output.write("\n")
        
        # Write recommendations
        output.write("## Recommendations\n")
        if report.recommendations:
            writer = csv.writer(output)
            writer.writerow(['#', 'Recommendation'])
            for idx, rec in enumerate(report.recommendations, 1):
                writer.writerow([idx, rec])
        
        return output.getvalue()
    
    def _export_executive_summary(self, report) -> str:
        """Export executive summary to CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Metric', 'Value'])
        
        # Summary data
        data = report.data
        writer.writerow(['Total Properties', data.get('total_properties', 0)])
        writer.writerow(['Fraud Detected', data.get('fraud_detected', 0)])
        writer.writerow(['Fraud Rate (%)', f"{data.get('fraud_rate', 0):.2f}"])
        
        # High-risk properties
        output.write("\n## High Risk Properties\n")
        high_risk = data.get('high_risk_properties', [])
        if high_risk:
            writer.writerow(['Property ID'])
            for prop_id in high_risk:
                writer.writerow([prop_id])
        
        return output.getvalue()
    
    def _export_generic(self, report) -> str:
        """Export generic report to CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Basic info
        writer.writerow(['Report ID', report.report_id])
        writer.writerow(['Type', report.report_type.value])
        writer.writerow(['Title', report.title])
        writer.writerow(['Created', report.created_at.isoformat()])
        
        return output.getvalue()
    
    def export_batch_analysis(self, results: List[Dict[str, Any]]) -> str:
        """
        Export batch analysis results to CSV
        
        Args:
            results: List of analysis results
        
        Returns:
            CSV string
        """
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        header = [
            'Property ID',
            'Survey Number',
            'Owner Name',
            'Risk Level',
            'Risk Score',
            'Fraud Detected',
            'Fraud Count',
            'Analysis Date'
        ]
        writer.writerow(header)
        
        # Data rows
        for result in results:
            property_data = result.get('property', {})
            writer.writerow([
                property_data.get('id', 'N/A'),
                property_data.get('survey_number', 'N/A'),
                property_data.get('owner_name', 'N/A'),
                result.get('risk_level', 'N/A'),
                result.get('risk_score', 0),
                'Yes' if result.get('fraud_detected', False) else 'No',
                len(result.get('fraud_flags', [])),
                result.get('analysis_date', datetime.now().isoformat())
            ])
        
        return output.getvalue()


# Export
__all__ = ['CSVExporter']