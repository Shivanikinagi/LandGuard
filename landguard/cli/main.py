"""
LandGuard CLI - Command-line interface for fraud detection.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import json
from typing import Optional

from core.landguard.analyzer import LandGuardAnalyzer
from core.models import LandRecord
from detector.extractors.json_extractor import JSONExtractor
from detector.extractors.csv_extractor import CSVExtractor
from detector.extractors.pdf_extractor import PDFExtractor
from detector.extractors.ocr_extractor import OCRExtractor

app = typer.Typer(help="🔍 LandGuard - Land Record Fraud Detection System")
console = Console()


@app.command()
def analyze(
    file_path: str = typer.Argument(..., help="Path to land record file"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output path for report"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Analyze a single land record file for fraud indicators."""
    
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        console.print(f"[red]✗[/red] File not found: {file_path}")
        raise typer.Exit(1)
    
    console.print(f"\n[cyan]🔍 Analyzing:[/cyan] {file_path_obj.name}")
    
    analyzer_config = None
    if config:
        config_path = Path(config)
        if config_path.exists():
            with open(config_path) as f:
                import yaml
                analyzer_config = yaml.safe_load(f)
    
    try:
        record = extract_record(file_path_obj)
    except Exception as e:
        console.print(f"[red]✗ Extraction failed:[/red] {e}")
        raise typer.Exit(1)
    
    analyzer = LandGuardAnalyzer(config=analyzer_config)
    report = analyzer.analyze_record(record)
    
    display_report(report, verbose=verbose)
    
    if output:
        output_path = Path(output)
        save_report(report, output_path)
        console.print(f"\n[green]✓[/green] Report saved to: {output_path}")


@app.command()
def batch(
    directory: str = typer.Argument(..., help="Directory containing land record files"),
    output: str = typer.Option("batch_report.json", "--output", "-o", help="Output report path"),
    pattern: str = typer.Option("*.json", "--pattern", "-p", help="File pattern to match"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path")
):
    """Analyze multiple land record files in batch mode."""
    
    directory_obj = Path(directory)
    
    if not directory_obj.exists() or not directory_obj.is_dir():
        console.print(f"[red]✗[/red] Directory not found: {directory}")
        raise typer.Exit(1)
    
    files = list(directory_obj.glob(pattern))
    
    if not files:
        console.print(f"[yellow]⚠[/yellow] No files found matching pattern: {pattern}")
        raise typer.Exit(0)
    
    console.print(f"\n[cyan]📂 Found {len(files)} file(s) to analyze[/cyan]\n")
    
    analyzer_config = None
    if config:
        config_path = Path(config)
        if config_path.exists():
            with open(config_path) as f:
                import yaml
                analyzer_config = yaml.safe_load(f)
    
    records = []
    with console.status("[bold cyan]Extracting records..."):
        for file_path in files:
            try:
                record = extract_record(file_path)
                records.append(record)
                console.print(f"[green]✓[/green] Extracted: {file_path.name}")
            except Exception as e:
                console.print(f"[red]✗[/red] Failed: {file_path.name} - {e}")
    
    if not records:
        console.print("[red]✗ No records extracted successfully[/red]")
        raise typer.Exit(1)
    
    console.print(f"\n[cyan]🔍 Running fraud detection on {len(records)} records...[/cyan]\n")
    analyzer = LandGuardAnalyzer(config=analyzer_config)
    
    output_path = Path(output)
    reports = analyzer.batch_analyze(records, report_path=str(output_path))
    
    display_batch_summary(reports)
    console.print(f"\n[green]✓[/green] Batch report saved to: {output_path}")


@app.command()
def config_template(
    output: str = typer.Option("landguard_config.yaml", "--output", "-o", help="Output path for config template")
):
    """Generate a template configuration file."""
    
    template = """# LandGuard Configuration Template

# Rapid Transfer Detection
rapid_transfer_days: 180
rapid_transfer_count: 2

# Large Transfer Detection
large_transfer_threshold: 10000000

# Name Matching
name_similarity_threshold: 85

# Date Validation
date_order_tolerance_days: 1
"""
    
    output_path = Path(output)
    with open(output_path, 'w') as f:
        f.write(template)
    
    console.print(f"[green]✓[/green] Config template saved to: {output_path}")


def extract_record(file_path: Path) -> LandRecord:
    """Extract land record from file based on type."""
    
    suffix = file_path.suffix.lower()
    
    if suffix == '.json':
        extractor = JSONExtractor()
    elif suffix == '.csv':
        extractor = CSVExtractor()
    elif suffix == '.pdf':
        extractor = PDFExtractor()
    elif suffix in ['.jpg', '.jpeg', '.png', '.tiff']:
        extractor = OCRExtractor()
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
    
    raw_data = extractor.extract(str(file_path))
    
    if isinstance(raw_data, dict):
        raw_data['source_file'] = str(file_path)
        return LandRecord(**raw_data)
    else:
        return LandRecord(
            land_id="UNKNOWN",
            raw_text=str(raw_data),
            source_file=str(file_path),
            extraction_confidence=0.3
        )


def display_report(report, verbose=False):
    """Display analysis report in terminal."""
    
    severity_colors = {
        "high": "red",
        "medium": "yellow",
        "low": "blue",
        "none": "green"
    }
    
    color = severity_colors.get(report.highest_severity, "white")
    
    console.print(Panel(
        f"[bold]Record:[/bold] {report.record_id}\n"
        f"[bold]Confidence Score:[/bold] {report.confidence:.2%}\n"
        f"[bold]Issues Found:[/bold] {report.total_issues}\n"
        f"[bold]Highest Severity:[/bold] [{color}]{report.highest_severity}[/{color}]",
        title="📊 Analysis Report",
        border_style=color
    ))
    
    if report.issues:
        table = Table(title="\n🚨 Detected Issues")
        table.add_column("Type", style="cyan")
        table.add_column("Severity", style="bold")
        table.add_column("Message", style="white")
        
        for issue in report.issues:
            severity_style = severity_colors.get(issue.severity, "white")
            table.add_row(
                issue.type,
                f"[{severity_style}]{issue.severity}[/{severity_style}]",
                issue.message
            )
        
        console.print(table)
        
        if verbose:
            console.print("\n[bold]📋 Evidence Details:[/bold]\n")
            for i, issue in enumerate(report.issues, 1):
                console.print(f"[cyan]{i}. {issue.type}[/cyan]")
                for evidence in issue.evidence:
                    console.print(f"   • {evidence}")
                console.print()
    else:
        console.print("\n[green]✓ No issues detected![/green]")


def display_batch_summary(reports):
    """Display summary of batch analysis."""
    
    total_records = len(reports)
    total_issues = sum(r.total_issues for r in reports)
    high_severity = sum(1 for r in reports if r.highest_severity == "high")
    medium_severity = sum(1 for r in reports if r.highest_severity == "medium")
    clean_records = sum(1 for r in reports if r.total_issues == 0)
    
    table = Table(title="📊 Batch Analysis Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="bold yellow")
    
    table.add_row("Total Records", str(total_records))
    table.add_row("Clean Records", f"[green]{clean_records}[/green]")
    table.add_row("Total Issues", str(total_issues))
    table.add_row("High Severity", f"[red]{high_severity}[/red]")
    table.add_row("Medium Severity", f"[yellow]{medium_severity}[/yellow]")
    
    console.print("\n")
    console.print(table)


def save_report(report, output_path: Path):
    """Save report to JSON file."""
    with open(output_path, 'w') as f:
        json.dump(report.dict(), f, indent=2, default=str)


if __name__ == "__main__":
    app()