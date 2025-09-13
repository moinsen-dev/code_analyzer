"""
Code Insight Analyzer CLI
"""
import typer
from typing import Optional, List
from pathlib import Path

from codeinsight.scanner import Scanner
from codeinsight.models.metrics import AnalysisReport
from codeinsight.exporters.json_exporter import JSONExporter
from codeinsight.exporters.csv_exporter import CSVExporter
from codeinsight.exporters.html_exporter import HTMLExporter

app = typer.Typer(
    name="codeinsight",
    help="A comprehensive code analysis tool",
    no_args_is_help=True
)

@app.command()
def analyze(
    path: Path = typer.Argument(..., help="Path to analyze"),
    complexity: bool = typer.Option(False, "--complexity", "-c", help="Include complexity analysis"),
    output: str = typer.Option("terminal", "--output", "-o", help="Output format (terminal, json, html, csv)"),
    export: List[str] = typer.Option([], "--export", "-e", help="Export formats (json, html, csv)"),
    export_dir: Path = typer.Option("./reports", "--export-dir", help="Directory for exports")
):
    """Analyze a codebase and display results."""
    typer.echo(f"Analyzing {path}")
    
    # Initialize scanner
    scanner = Scanner()
    
    # Perform analysis
    report = scanner.analyze(path, include_complexity=complexity)
    
    # Display output based on format
    if output == "terminal":
        _display_terminal(report, complexity)
    elif output == "json":
        typer.echo(report.json())
    
    # Export if requested
    if export:
        # Flatten the export list (handle comma-separated values)
        flattened_export = []
        for item in export:
            flattened_export.extend(item.split(','))
        _export_results(report, flattened_export, export_dir)

def _display_terminal(report: AnalysisReport, show_complexity: bool):
    """Display results in terminal with Rich formatting."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        
        console = Console()
        
        # Display summary panel
        console.print(Panel(f"[bold]Code Insight Analysis[/bold]\n"
                           f"Project: {report.project_path}\n"
                           f"Files: {report.total_files}\n"
                           f"Lines of Code: {report.total_lines:,}\n"
                           f"Total Size: {report.total_size:,} bytes"))
        
        # Display top files
        if show_complexity:
            table = Table(title="Top Files by Line Count (with Complexity)")
            table.add_column("File", style="cyan")
            table.add_column("Lines", justify="right", style="green")
            table.add_column("Size", justify="right", style="magenta")
            table.add_column("Complexity", justify="right", style="yellow")
        else:
            table = Table(title="Top Files by Line Count")
            table.add_column("File", style="cyan")
            table.add_column("Lines", justify="right", style="green")
            table.add_column("Size", justify="right", style="magenta")
        
        for file_insight in report.top_files[:10]:
            if show_complexity and file_insight.complexity_metrics:
                complexity_str = f"{file_insight.complexity_metrics.cyclomatic_complexity:.1f}"
                table.add_row(
                    str(file_insight.file_metrics.relative_path),
                    str(file_insight.file_metrics.lines_of_code),
                    f"{file_insight.file_metrics.size_bytes:,} bytes",
                    complexity_str
                )
            else:
                table.add_row(
                    str(file_insight.file_metrics.relative_path),
                    str(file_insight.file_metrics.lines_of_code),
                    f"{file_insight.file_metrics.size_bytes:,} bytes"
                )
        
        console.print(table)
        
    except ImportError:
        # Fallback to basic output
        print(f"Analysis Report for {report.project_path}")
        print(f"Total Files: {report.total_files}")
        print(f"Total Lines: {report.total_lines}")
        print(f"Total Size: {report.total_size} bytes")
        print("\nTop Files:")
        for file_insight in report.top_files[:10]:
            if show_complexity and file_insight.complexity_metrics:
                print(f"  {file_insight.file_metrics.relative_path}: "
                      f"{file_insight.file_metrics.lines_of_code} lines "
                      f"(Complexity: {file_insight.complexity_metrics.cyclomatic_complexity:.1f})")
            else:
                print(f"  {file_insight.file_metrics.relative_path}: "
                      f"{file_insight.file_metrics.lines_of_code} lines")

def _export_results(report: AnalysisReport, formats: List[str], export_dir: Path):
    """Export results to specified formats."""
    export_dir.mkdir(exist_ok=True)
    
    for fmt in formats:
        try:
            if fmt == "json":
                exporter = JSONExporter()
                exporter.export(report, export_dir / "report.json")
                typer.echo(f"Exported JSON report to {export_dir / 'report.json'}")
            elif fmt == "csv":
                exporter = CSVExporter()
                exporter.export(report, export_dir / "report.csv")
                typer.echo(f"Exported CSV report to {export_dir / 'report.csv'}")
            elif fmt == "html":
                exporter = HTMLExporter()
                exporter.export(report, export_dir / "report.html")
                typer.echo(f"Exported HTML report to {export_dir / 'report.html'}")
            else:
                typer.echo(f"Warning: Unknown export format '{fmt}'")
        except Exception as e:
            typer.echo(f"Error exporting to {fmt}: {e}")

@app.command()
def compare(
    report1: Path = typer.Argument(..., help="First report file"),
    report2: Path = typer.Argument(..., help="Second report file")
):
    """Compare two analysis reports."""
    typer.echo(f"Comparing {report1} and {report2}")
    # TODO: Implement comparison functionality

if __name__ == "__main__":
    app()
