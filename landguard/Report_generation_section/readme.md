# 🚀 Phase 4: Advanced Reporting System - Setup Guide

## 📁 Step 1: Create Directory Structure

```bash
# From your project root
mkdir -p reporting/exporters
mkdir -p reporting/templates
mkdir -p reports

# Create __init__.py files
touch reporting/__init__.py
touch reporting/exporters/__init__.py
```

## 📝 Step 2: Copy Files

Copy these files from the artifacts above:

```
reporting/
├── __init__.py
├── base_report.py              # Artifact: base_report
├── report_generator.py         # Artifact: report_generator
└── exporters/
    ├── __init__.py
    ├── html_exporter.py        # Artifact: html_exporter
    ├── csv_exporter.py         # Artifact: csv_exporter
    └── pdf_exporter.py         # Artifact: pdf_exporter

demo_reporting.py               # Artifact: demo_reporting
```

## 🔧 Step 3: Create __init__.py Files

### `reporting/__init__.py`

```python
"""
LandGuard Phase 4: Advanced Reporting System
"""

from .report_generator import ReportGenerator
from .base_report import (
    BaseReport,
    ReportType,
    ReportFormat,
    RiskLevel,
    FraudAnalysisReport,
    ExecutiveSummaryReport
)

__version__ = "1.0.0"
__all__ = [
    'ReportGenerator',
    'BaseReport',
    'ReportType',
    'ReportFormat',
    'RiskLevel',
    'FraudAnalysisReport',
    'ExecutiveSummaryReport'
]
```

### `reporting/exporters/__init__.py`

```python
"""Report exporters"""

from .html_exporter import HTMLExporter
from .csv_exporter import CSVExporter
from .pdf_exporter import PDFExporter

__all__ = ['HTMLExporter', 'CSVExporter', 'PDFExporter']
```

## 📦 Step 4: Install Dependencies

```bash
# Required (already installed from previous phases)
pip install rich

# Optional: For PDF generation (choose one)
# Option 1: WeasyPrint (recommended)
pip install weasyprint

# Option 2: pdfkit + wkhtmltopdf
pip install pdfkit
# Download wkhtmltopdf from: https://wkhtmltopdf.org/downloads.html

# Note: PDF generation will work without these,
# but will return HTML files with conversion instructions
```

## 🚀 Step 5: Run the Demo

```bash
python demo_reporting.py
```

## ✅ Expected Output

```
🎉 LandGuard Phase 4: Advanced Reporting System Demo
======================================================================

📊 Fraud Analysis Report Generation
======================================================================

Creating fraud analysis report...

          Report Summary
┌─────────────────┬────────────────────────┐
│ Field           │ Value                  │
├─────────────────┼────────────────────────┤
│ Report ID       │ RPT-20241127143022-... │
│ Property ID     │ PROP-2024-001          │
│ Risk Level      │ HIGH                   │
│ Findings        │ 3                      │
│ Recommendations │ 5                      │
└─────────────────┴────────────────────────┘

💾 Exporting to Multiple Formats
======================================================================

     Export Results
┌────────┬──────────┬──────────────────────────┐
│ Format │ Status   │ File Path                │
├────────┼──────────┼──────────────────────────┤
│ HTML   │ ✅ Success│ reports/RPT-xxx.html    │
│ CSV    │ ✅ Success│ reports/RPT-xxx.csv     │
│ JSON   │ ✅ Success│ reports/RPT-xxx.json    │
│ PDF    │ ✅ Success│ reports/RPT-xxx.pdf     │
└────────┴──────────┴──────────────────────────┘

...

✨ Demo Complete
======================================================================
✅ All reports generated successfully!
```

## 📂 What Gets Created

After running the demo, you'll find:

```
reports/
├── RPT-20241127143022-1234_20241127_143022.html
├── RPT-20241127143022-1234_20241127_143022.csv
├── RPT-20241127143022-1234_20241127_143022.json
├── RPT-20241127143022-1234_20241127_143022.pdf
├── RPT-20241127143025-5678_20241127_143025.html
├── RPT-20241127143025-5678_20241127_143025.csv
└── batch_analysis_20241127_143030.csv
```

## 🎯 Quick Usage Examples

### Generate Fraud Analysis Report

```python
from reporting.report_generator import ReportGenerator
from reporting.base_report import ReportFormat

# Create generator
generator = ReportGenerator(output_dir="reports")

# Your analysis results
analysis_results = {
    'property': {'id': 'PROP-001', 'owner_name': 'John Doe', ...},
    'fraud_detected': True,
    'risk_score': 85,
    'fraud_flags': [...],
    'recommendations': [...]
}

# Create report
report = generator.create_fraud_analysis_report(
    property_id='PROP-001',
    analysis_results=analysis_results
)

# Export to HTML
html_path = generator.export(report, ReportFormat.HTML)
print(f"Report saved: {html_path}")

# Or export to all formats
paths = generator.export_all_formats(report)
```

### Generate Executive Summary

```python
# Batch analysis results
batch_results = [result1, result2, result3, ...]

# Create summary
summary = generator.create_executive_summary(batch_results)

# Export
generator.export(summary, ReportFormat.HTML)
generator.export(summary, ReportFormat.CSV)
```

### Export Batch to CSV

```python
# Export multiple analysis results to single CSV
csv_path = generator.export_batch_csv(batch_results)
```

## 📊 Report Features

### HTML Reports Include:
- ✅ Professional styling with gradients
- ✅ Risk level badges with color coding
- ✅ Property information cards
- ✅ Detailed findings with severity levels
- ✅ Actionable recommendations
- ✅ Print-friendly layout
- ✅ Responsive design

### CSV Reports Include:
- ✅ Property details
- ✅ Findings list
- ✅ Recommendations
- ✅ Batch analysis data
- ✅ Excel-compatible format

### PDF Reports Include:
- ✅ Professional formatting
- ✅ Embedded charts (if libraries available)
- ✅ Page breaks
- ✅ Headers and footers

## 🔧 Customization

### Custom Report Template

```python
from reporting.base_report import BaseReport, ReportType

class CustomReport(BaseReport):
    def __init__(self, data):
        super().__init__(
            report_type=ReportType.DETAILED_ANALYSIS,
            title="Custom Analysis Report",
            description="Your custom report"
        )
        # Add your custom logic
        self.add_data('custom_field', data)
    
    def generate(self, format):
        from reporting.report_generator import ReportGenerator
        generator = ReportGenerator()
        return generator.export(self, format)
```

### Modify HTML Template

Edit `reporting/exporters/html_exporter.py` to customize:
- Colors and styling
- Layout and structure
- Additional sections
- Chart types

## 🎨 Styling Customization

The HTML reports use inline CSS. Key colors:

```css
Primary: #667eea (purple-blue)
Secondary: #764ba2 (purple)
Success: #28a745 (green)
Warning: #ffc107 (yellow)
Danger: #dc3545 (red)
```

Change these in `html_exporter.py` to match your brand.

## 🐛 Troubleshooting

### PDF Generation Issues

If PDF generation fails:
1. Install WeasyPrint: `pip install weasyprint`
2. Or use browser: Open HTML file → Print → Save as PDF
3. Reports fall back to HTML with instructions

### Import Errors

```bash
# Make sure you're in the correct directory
cd /path/to/your/project

# Check Python path
python -c "import sys; print(sys.path)"
```

### Permission Errors

```bash
# Ensure reports directory is writable
mkdir -p reports
chmod 755 reports
```

## 🎉 You're Done!

Run the demo:
```bash
python demo_reporting.py
```

Check the `reports/` folder for your generated reports!

## 📚 Next Steps

1. **Integrate with Analyzer**: Connect to your fraud detection system
2. **Email Reports**: Add email functionality (Phase 4 extension)
3. **Dashboard**: Create interactive web dashboard
4. **Scheduled Reports**: Set up automated report generation
5. **Custom Templates**: Design your own report layouts


# Phase 4: Advanced Reporting System - Structure

```
landguard/
├── reporting/
│   ├── __init__.py
│   ├── base_report.py              # Base report class
│   ├── report_generator.py         # Main report generator
│   │
│   ├── exporters/
│   │   ├── __init__.py
│   │   ├── html_exporter.py        # HTML report generation
│   │   ├── pdf_exporter.py         # PDF report generation
│   │   ├── csv_exporter.py         # CSV export
│   │   ├── json_exporter.py        # JSON export
│   │   └── excel_exporter.py       # Excel export
│   │
│   ├── templates/
│   │   ├── fraud_report.html       # Fraud analysis report template
│   │   ├── summary_report.html     # Executive summary template
│   │   ├── detailed_report.html    # Detailed analysis template
│   │   └── dashboard.html          # Interactive dashboard template
│   │
│   ├── visualizations/
│   │   ├── __init__.py
│   │   ├── charts.py               # Chart generation
│   │   ├── graphs.py               # Graph generation
│   │   └── maps.py                 # Geographic visualizations
│   │
│   ├── dashboard/
│   │   ├── __init__.py
│   │   ├── dashboard_server.py     # Web dashboard server
│   │   └── static/
│   │       ├── css/
│   │       │   └── dashboard.css
│   │       └── js/
│   │           └── dashboard.js
│   │
│   └── email/
│       ├── __init__.py
│       └── email_sender.py         # Email notification system
│
└── reporting/config/
    └── report_config.yaml           # Report configuration
```

## Features

### 1. Multiple Export Formats
- HTML reports with embedded charts
- PDF reports with professional styling
- CSV data exports
- Excel workbooks with multiple sheets
- JSON for API integration

### 2. Visualizations
- Fraud type distribution (pie charts)
- Risk score trends (line charts)
- Geographic fraud hotspots (maps)
- Property value analysis (bar charts)
- Timeline visualizations

### 3. Interactive Dashboard
- Real-time fraud monitoring
- Filterable data tables
- Interactive charts
- Search and export functionality
- Responsive design

### 4. Email Notifications
- Automated report delivery
- Alert notifications for high-risk cases
- Scheduled report sending
- Attachment support