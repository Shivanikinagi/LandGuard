"""
LandGuard Phase 4: Reporting System Demo
Demonstrates report generation in multiple formats
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from datetime import datetime
import os

from reporting.report_generator import ReportGenerator
from reporting.base_report import ReportFormat, RiskLevel


console = Console()


def print_header(title: str):
    """Print section header"""
    console.print(f"\n{'='*70}")
    console.print(f"[bold cyan]{title}[/bold cyan]")
    console.print(f"{'='*70}\n")


def create_sample_analysis_results():
    """Create sample fraud analysis results"""
    return {
        'property': {
            'id': 'PROP-2024-001',
            'survey_number': '123/4',
            'owner_name': 'Rajesh Kumar',
            'area': 2500,
            'location': 'Mumbai, Maharashtra',
            'property_type': 'Residential',
            'registration_date': '2020-05-15',
            'market_value': 15000000
        },
        'fraud_detected': True,
        'risk_score': 75,
        'fraud_flags': [
            {
                'type': 'Price Manipulation',
                'description': 'Sale price significantly below market value',
                'severity': 'high',
                'evidence': {
                    'declared_price': 8000000,
                    'market_price': 15000000,
                    'deviation': '47%'
                }
            },
            {
                'type': 'Ownership Mismatch',
                'description': 'Discrepancy in ownership records',
                'severity': 'critical',
                'evidence': {
                    'registry_owner': 'Rajesh Kumar',
                    'document_owner': 'R. Kumar'
                }
            },
            {
                'type': 'Rapid Transaction',
                'description': 'Property sold multiple times within 6 months',
                'severity': 'medium',
                'evidence': {
                    'transaction_count': 3,
                    'time_period': '180 days'
                }
            }
        ],
        'recommendations': [
            'Verify ownership documents from government registry',
            'Conduct physical inspection of the property',
            'Cross-check with tax assessment records',
            'Interview previous owners',
            'Legal consultation recommended before proceeding'
        ]
    }


def demo_fraud_analysis_report():
    """Demo fraud analysis report generation"""
    print_header("📊 Fraud Analysis Report Generation")
    
    generator = ReportGenerator(output_dir="reports")
    
    console.print("[yellow]Creating fraud analysis report...[/yellow]\n")
    
    # Create sample data
    analysis_results = create_sample_analysis_results()
    property_id = analysis_results['property']['id']
    
    # Create report
    report = generator.create_fraud_analysis_report(
        property_id=property_id,
        analysis_results=analysis_results
    )
    
    # Show report summary
    summary = report.get_summary()
    
    table = Table(title="Report Summary", box=box.ROUNDED)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Report ID", summary['report_id'])
    table.add_row("Property ID", property_id)
    table.add_row("Risk Level", summary['risk_level'].upper())
    table.add_row("Findings", str(summary['findings_count']))
    table.add_row("Recommendations", str(summary['recommendations_count']))
    table.add_row("Created At", summary['created_at'][:19])
    
    console.print(table)
    
    return report, generator


def demo_export_formats(report, generator):
    """Demo exporting in multiple formats"""
    print_header("💾 Exporting to Multiple Formats")
    
    console.print("[yellow]Exporting report in all formats...[/yellow]\n")
    
    # Export to all formats
    results = generator.export_all_formats(report)
    
    # Show results
    table = Table(title="Export Results", box=box.ROUNDED)
    table.add_column("Format", style="cyan", width=15)
    table.add_column("Status", style="bold", width=15)
    table.add_column("File Path", style="dim")
    
    for format_name, filepath in results.items():
        if filepath:
            status = "✅ Success"
            # Get relative path
            rel_path = os.path.relpath(filepath)
        else:
            status = "❌ Failed"
            rel_path = "N/A"
        
        table.add_row(format_name.upper(), status, rel_path)
    
    console.print(table)
    
    return results


def demo_executive_summary():
    """Demo executive summary report"""
    print_header("📈 Executive Summary Report")
    
    generator = ReportGenerator(output_dir="reports")
    
    console.print("[yellow]Creating executive summary...[/yellow]\n")
    
    # Create sample batch results
    batch_results = []
    for i in range(1, 11):
        result = create_sample_analysis_results()
        result['property']['id'] = f'PROP-2024-{i:03d}'
        result['fraud_detected'] = i % 3 == 0  # Every 3rd property has fraud
        result['risk_score'] = 30 + (i * 7) % 60
        batch_results.append(result)
    
    # Create executive summary
    summary_report = generator.create_executive_summary(batch_results)
    
    # Export to HTML and CSV
    html_path = generator.export(summary_report, ReportFormat.HTML)
    csv_path = generator.export(summary_report, ReportFormat.CSV)
    
    # Show results
    data = summary_report.data
    
    stats_table = Table(title="Analysis Statistics", box=box.DOUBLE)
    stats_table.add_column("Metric", style="cyan", width=25)
    stats_table.add_column("Value", style="bold yellow", justify="right")
    
    stats_table.add_row("Total Properties", str(data['total_properties']))
    stats_table.add_row("Fraud Detected", str(data['fraud_detected']))
    stats_table.add_row("Fraud Rate", f"{data['fraud_rate']:.1f}%")
    stats_table.add_row("High Risk Properties", str(len(data['high_risk_properties'])))
    
    console.print(stats_table)
    
    console.print(f"\n[green]✅ HTML Report:[/green] {os.path.relpath(html_path)}")
    console.print(f"[green]✅ CSV Export:[/green] {os.path.relpath(csv_path)}")


def demo_batch_csv_export():
    """Demo batch CSV export"""
    print_header("📑 Batch CSV Export")
    
    generator = ReportGenerator(output_dir="reports")
    
    console.print("[yellow]Exporting batch analysis to CSV...[/yellow]\n")
    
    # Create batch results
    batch_results = []
    for i in range(1, 26):
        result = create_sample_analysis_results()
        result['property']['id'] = f'PROP-2024-{i:03d}'
        result['property']['survey_number'] = f'{100+i}/{i%10+1}'
        result['fraud_detected'] = i % 4 == 0
        result['risk_score'] = 20 + (i * 5) % 70
        batch_results.append(result)
    
    # Export to CSV
    csv_path = generator.export_batch_csv(batch_results)
    
    console.print(f"[green]✅ Exported {len(batch_results)} properties to CSV[/green]")
    console.print(f"[cyan]File:[/cyan] {os.path.relpath(csv_path)}\n")
    
    # Show preview
    console.print("[yellow]CSV Preview (first 5 rows):[/yellow]")
    with open(csv_path, 'r') as f:
        lines = f.readlines()[:6]  # Header + 5 rows
        for line in lines:
            console.print(f"[dim]{line.rstrip()}[/dim]")


def show_report_files(generator):
    """Show all generated report files"""
    print_header("📁 Generated Reports")
    
    reports = generator.list_reports()
    
    if not reports:
        console.print("[yellow]No reports found[/yellow]")
        return
    
    table = Table(title=f"Found {len(reports)} Report(s)", box=box.ROUNDED)
    table.add_column("#", style="cyan", width=5)
    table.add_column("File Name", style="white")
    table.add_column("Format", style="yellow", width=10)
    table.add_column("Size", style="green", justify="right", width=12)
    
    for idx, filepath in enumerate(reports[:10], 1):  # Show first 10
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1][1:]  # Get extension without dot
        
        try:
            size = os.path.getsize(filepath)
            size_str = f"{size:,} B"
            if size > 1024:
                size_str = f"{size/1024:.1f} KB"
            if size > 1024*1024:
                size_str = f"{size/(1024*1024):.1f} MB"
        except:
            size_str = "N/A"
        
        table.add_row(str(idx), filename, ext.upper(), size_str)
    
    console.print(table)
    
    if len(reports) > 10:
        console.print(f"\n[dim]... and {len(reports)-10} more files[/dim]")


def main():
    """Main demo function"""
    console.print(f"\n[bold magenta] {"="*70} [/bold magenta]\n")
    console.print("🎉 LandGuard Phase 4: Advanced Reporting System Demo")
    console.print(f"\n[bold magenta] {"="*70} [/bold magenta]\n")
    
    try:
        # Demo 1: Fraud Analysis Report
        report, generator = demo_fraud_analysis_report()
        
        # Demo 2: Export to Multiple Formats
        export_results = demo_export_formats(report, generator)
        
        # Demo 3: Executive Summary
        demo_executive_summary()
        
        # Demo 4: Batch CSV Export
        demo_batch_csv_export()
        
        # Demo 5: Show all reports
        show_report_files(generator)
        
        # Final message
        print_header("✨ Demo Complete")
        
        panel = Panel(
            """[bold green]✅ All reports generated successfully![/bold green]

[yellow]What was created:[/yellow]
  • Fraud Analysis Reports (HTML, PDF, CSV, JSON)
  • Executive Summary Reports  
  • Batch CSV Exports
  • All files saved in 'reports/' directory

[cyan]Key Features:[/cyan]
  • Multiple export formats (HTML, PDF, CSV, JSON)
  • Professional report templates
  • Risk level classification
  • Detailed findings and recommendations
  • Batch analysis support

[yellow]Next Steps:[/yellow]
  1. Check the 'reports/' folder for generated files
  2. Open HTML files in your browser
  3. Import CSV files into Excel/Google Sheets
  4. Integrate with your fraud detection analyzer
  5. Customize report templates as needed

[dim]Tip: HTML files can be printed to PDF from your browser[/dim]""",
            title="[bold cyan]Success![/bold cyan]",
            border_style="cyan"
        )
        console.print(panel)
        
        console.print(f"\n[green]📂 Reports saved to:[/green] {os.path.abspath('reports')}\n")
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
    
    console.print()


if __name__ == "__main__":
    main()