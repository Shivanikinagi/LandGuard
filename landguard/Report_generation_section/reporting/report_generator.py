"""
LandGuard Phase 4: Report Generator
Main interface for generating reports in multiple formats
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json
import logging

from .base_report import BaseReport, ReportFormat, FraudAnalysisReport, ExecutiveSummaryReport
from .exporters.html_exporter import HTMLExporter
from .exporters.csv_exporter import CSVExporter
from .exporters.pdf_exporter import PDFExporter


logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Main report generation interface
    Handles creating and exporting reports in multiple formats
    """
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize exporters
        self.html_exporter = HTMLExporter()
        self.csv_exporter = CSVExporter()
        self.pdf_exporter = PDFExporter()
        
        logger.info(f"ReportGenerator initialized. Output directory: {self.output_dir}")
    
    def create_fraud_analysis_report(
        self,
        property_id: str,
        analysis_results: Dict[str, Any]
    ) -> FraudAnalysisReport:
        """
        Create fraud analysis report from analysis results
        
        Args:
            property_id: Property identifier
            analysis_results: Fraud analysis results
        
        Returns:
            FraudAnalysisReport instance
        """
        logger.info(f"Creating fraud analysis report for property: {property_id}")
        
        report = FraudAnalysisReport(
            property_id=property_id,
            analysis_results=analysis_results
        )
        
        return report
    
    def create_executive_summary(
        self,
        analysis_results: List[Dict[str, Any]]
    ) -> ExecutiveSummaryReport:
        """
        Create executive summary from batch analysis results
        
        Args:
            analysis_results: List of analysis results
        
        Returns:
            ExecutiveSummaryReport instance
        """
        logger.info(f"Creating executive summary for {len(analysis_results)} properties")
        
        total_properties = len(analysis_results)
        fraud_detected = sum(1 for r in analysis_results if r.get('fraud_detected', False))
        high_risk_properties = [
            r.get('property', {}).get('id', 'Unknown')
            for r in analysis_results
            if r.get('risk_score', 0) >= 70
        ]
        
        report = ExecutiveSummaryReport(
            total_properties=total_properties,
            fraud_detected=fraud_detected,
            high_risk_properties=high_risk_properties
        )
        
        return report
    
    def export(
        self,
        report: BaseReport,
        format: ReportFormat,
        filename: Optional[str] = None
    ) -> str:
        """
        Export report to specified format and save to file
        
        Args:
            report: Report to export
            format: Output format
            filename: Optional custom filename
        
        Returns:
            Path to saved file
        """
        logger.info(f"Exporting report {report.report_id} to {format.value}")
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report.report_id}_{timestamp}.{format.value}"
        
        filepath = self.output_dir / filename
        
        # Export based on format
        if format == ReportFormat.HTML:
            content = self.html_exporter.export(report)
            filepath.write_text(content, encoding='utf-8')
        
        elif format == ReportFormat.CSV:
            content = self.csv_exporter.export(report)
            filepath.write_text(content, encoding='utf-8')
        
        elif format == ReportFormat.PDF:
            content = self.pdf_exporter.export(report)
            filepath.write_bytes(content)
        
        elif format == ReportFormat.JSON:
            content = json.dumps(report.to_dict(), indent=2)
            filepath.write_text(content, encoding='utf-8')
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Report saved to: {filepath}")
        return str(filepath)
    
    def export_all_formats(
        self,
        report: BaseReport,
        base_filename: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Export report in all supported formats
        
        Args:
            report: Report to export
            base_filename: Base filename (without extension)
        
        Returns:
            Dictionary mapping format to filepath
        """
        logger.info(f"Exporting report {report.report_id} in all formats")
        
        if not base_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"{report.report_id}_{timestamp}"
        
        results = {}
        
        for format in [ReportFormat.HTML, ReportFormat.CSV, ReportFormat.JSON, ReportFormat.PDF]:
            try:
                filename = f"{base_filename}.{format.value}"
                filepath = self.export(report, format, filename)
                results[format.value] = filepath
            except Exception as e:
                logger.error(f"Failed to export to {format.value}: {e}")
                results[format.value] = None
        
        return results
    
    def export_batch_csv(
        self,
        analysis_results: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> str:
        """
        Export batch analysis results to CSV
        
        Args:
            analysis_results: List of analysis results
            filename: Optional filename
        
        Returns:
            Path to saved file
        """
        logger.info(f"Exporting batch analysis ({len(analysis_results)} properties) to CSV")
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_analysis_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        content = self.csv_exporter.export_batch_analysis(analysis_results)
        filepath.write_text(content, encoding='utf-8')
        
        logger.info(f"Batch CSV saved to: {filepath}")
        return str(filepath)
    
    def get_report_summary(self, report: BaseReport) -> Dict[str, Any]:
        """
        Get summary information about a report
        
        Args:
            report: Report instance
        
        Returns:
            Summary dictionary
        """
        return report.get_summary()
    
    def list_reports(self, format: Optional[ReportFormat] = None) -> List[str]:
        """
        List all saved reports
        
        Args:
            format: Optional filter by format
        
        Returns:
            List of report filepaths
        """
        if format:
            pattern = f"*.{format.value}"
        else:
            pattern = "*.*"
        
        reports = [str(f) for f in self.output_dir.glob(pattern) if f.is_file()]
        return sorted(reports, reverse=True)


# Export
__all__ = ['ReportGenerator']