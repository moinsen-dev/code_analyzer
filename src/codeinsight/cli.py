"""
Code Insight Analyzer CLI
"""

import typer
import json
import signal
import sys
from typing import List, Dict, Any
from pathlib import Path

from codeinsight.scanner import Scanner
from codeinsight.watcher import CodeWatcher
from codeinsight.models.metrics import AnalysisReport
from codeinsight.exporters.json_exporter import JSONExporter
from codeinsight.exporters.csv_exporter import CSVExporter
from codeinsight.exporters.html_exporter import HTMLExporter
from codeinsight.analysis.comparator import ReportComparator

app = typer.Typer(
    name="code_analyzer",
    help="A comprehensive code analysis tool",
)


@app.command()
def init(
    path: Path = typer.Argument(".", help="Path to initialize configuration"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing configuration file"
    ),
) -> None:
    """Initialize a .code_analyzer.yml configuration file in the project directory."""
    config_path = path / ".code_analyzer.yml"

    if config_path.exists() and not force:
        typer.echo(f"Configuration file already exists at {config_path}")
        typer.echo("Use --force to overwrite the existing file.")
        raise typer.Exit(1)

    # Default configuration content
    default_config = """version: 1.0

# Language-specific settings
languages:
  python:
    max_line_length: 88
    complexity_threshold: 10
  typescript:
    max_line_length: 100
    complexity_threshold: 15
  javascript:
    max_line_length: 100
    complexity_threshold: 15

# Analysis rules
analysis:
  ignore_patterns:
    - "*.generated.*"
    - "*_pb2.py"
    - "*.min.js"
    - "node_modules/"
    - ".git/"
  
  complexity:
    include_docstrings: false
    count_assertions: true
  
  thresholds:
    file_too_long: 500
    function_too_complex: 20
    class_too_large: 1000

# Output preferences
output:
  format: "terminal"  # terminal, json, html, csv
  theme: "monokai"
  show_recommendations: true
  export_path: "./reports"
"""

    try:
        with open(config_path, "w") as f:
            f.write(default_config)
        typer.echo(f"Created .code_analyzer.yml configuration file at {config_path}")
    except Exception as e:
        typer.echo(f"Error creating configuration file: {e}")
        raise typer.Exit(1)


@app.command()
def analyze(
    path: Path = typer.Argument(..., help="Path to analyze"),
    complexity: bool = typer.Option(
        False, "--complexity", "-c", help="Include complexity analysis"
    ),
    output: str = typer.Option(
        "terminal", "--output", "-o", help="Output format (terminal, json, html, csv)"
    ),
    export: List[str] = typer.Option(
        [], "--export", "-e", help="Export formats (json, html, csv)"
    ),
    export_dir: Path = typer.Option(
        "./reports", "--export-dir", help="Directory for exports"
    ),
    top_files: int = typer.Option(
        20, "--top-files", "-t", help="Number of top files to display [default: 20]"
    ),
) -> None:
    """Analyze a codebase and display results."""
    typer.echo(f"Analyzing {path}")

    # Initialize scanner with the project path
    scanner = Scanner(path)

    # Perform analysis
    report = scanner.analyze(path, include_complexity=complexity)

    # Display output based on format
    if output == "terminal":
        _display_terminal(report, complexity, top_files)
    elif output == "json":
        typer.echo(report.json())

    # Export if requested
    if export:
        # Flatten the export list (handle comma-separated values)
        flattened_export = []
        for item in export:
            flattened_export.extend(item.split(","))
        _export_results(report, flattened_export, export_dir)


def _display_terminal(
    report: AnalysisReport, show_complexity: bool, top_files: int = 20
) -> None:
    """Display results in terminal with Rich formatting."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel

        console = Console()

        # Display main header
        console.print(
            Panel(
                f"[bold]Code Insight Analyzer v1.0[/bold]\n"
                f"[cyan]Project:[/cyan] {report.project_path}",
                expand=False,
            )
        )

        # Display analysis summary
        console.print("\n[bold]📊 Analysis Summary[/bold]")
        console.print("─" * 18)

        summary_table = Table(show_header=False, box=None, padding=(0, 2))
        summary_table.add_column(style="cyan")
        summary_table.add_column(style="white", justify="right")

        summary_table.add_row("Total Files:", f"{report.total_files:,}")
        summary_table.add_row("Lines of Code:", f"{report.total_lines:,}")
        summary_table.add_row("Total Size:", f"{report.total_size:,} bytes")

        # Language distribution summary
        if report.language_distribution:
            lang_summary = []
            for lang, count in sorted(
                report.language_distribution.items(), key=lambda x: x[1], reverse=True
            )[:3]:
                percentage = (count / report.total_files) * 100
                lang_summary.append(f"{lang.value} ({percentage:.0f}%)")
            summary_table.add_row("Languages:", ", ".join(lang_summary))

        console.print(summary_table)

        # Display top complex files if complexity is enabled
        if show_complexity:
            complex_files = [f for f in report.top_files if f.complexity_metrics]
            if complex_files:
                console.print("\n[bold]🔥 Complexity Hotspots (Top 5)[/bold]")
                console.print("─" * 36)

                complexity_table = Table(show_header=True)
                complexity_table.add_column("File", style="cyan")
                complexity_table.add_column("Lines", justify="right", style="green")
                complexity_table.add_column(
                    "Complexity", justify="right", style="yellow"
                )
                complexity_table.add_column("Risk Level", justify="center")

                for file_insight in complex_files[:5]:
                    complexity = file_insight.complexity_metrics
                    if complexity is not None:
                        cyclomatic = complexity.cyclomatic_complexity

                        # Determine risk level
                        if cyclomatic > 20:
                            risk_level = "[red]🔴 High[/red]"
                        elif cyclomatic > 10:
                            risk_level = "[orange]🟠 Medium[/orange]"
                        elif cyclomatic > 5:
                            risk_level = "[yellow]🟡 Low[/yellow]"
                        else:
                            risk_level = "[green]🟢 Good[/green]"

                        complexity_table.add_row(
                            str(file_insight.file_metrics.relative_path),
                            str(file_insight.file_metrics.lines_of_code),
                            f"{cyclomatic:.1f}",
                            risk_level,
                        )
                    else:
                        # Handle case where complexity metrics are not available
                        complexity_table.add_row(
                            str(file_insight.file_metrics.relative_path),
                            str(file_insight.file_metrics.lines_of_code),
                            "-",
                            "[grey]N/A[/grey]",
                        )

                console.print(complexity_table)

        # Display top files by line count
        console.print(f"\n[bold]📁 Top Files by Line Count (Top {top_files})[/bold]")
        console.print("─" * (31 + len(str(top_files))))

        files_table = Table(show_header=True)
        files_table.add_column("File", style="cyan")
        files_table.add_column("Lines", justify="right", style="green")
        files_table.add_column("Size", justify="right", style="magenta")

        for file_insight in report.top_files[:top_files]:
            files_table.add_row(
                str(file_insight.file_metrics.relative_path),
                str(file_insight.file_metrics.lines_of_code),
                f"{file_insight.file_metrics.size_bytes:,} bytes",
            )

        console.print(files_table)

        # Display code smells if any
        smells_found = []
        for file_insight in report.top_files:
            if file_insight.code_smells:
                smells_found.extend(
                    [
                        (file_insight.file_metrics.relative_path, smell)
                        for smell in file_insight.code_smells
                    ]
                )

        if smells_found:
            console.print("\n[bold]💡 Code Smells Detected[/bold]")
            console.print("─" * 24)

            smell_table = Table(show_header=True)
            smell_table.add_column("File", style="cyan")
            smell_table.add_column("Smell", style="yellow")

            for file_path, smell in smells_found[:10]:  # Show top 10 smells
                smell_table.add_row(file_path, smell)

            console.print(smell_table)

        # Display code duplications if any
        duplications_found = []
        for file_insight in report.top_files:
            if file_insight.duplications:
                for duplication in file_insight.duplications:
                    duplications_found.append(
                        (file_insight.file_metrics.relative_path, duplication)
                    )

        if duplications_found:
            console.print("\n[bold]🔍 Code Duplications Detected[/bold]")
            console.print("─" * 30)

            dup_table = Table(show_header=True)
            dup_table.add_column("File", style="cyan")
            dup_table.add_column("Duplication", style="yellow")

            for file_path, duplication in duplications_found[
                :10
            ]:  # Show top 10 duplications
                dup_info = f"{duplication.type} '{duplication.name}' ({duplication.count} duplicates)"
                dup_table.add_row(file_path, dup_info)

            console.print(dup_table)

        # Display recommendations if any
        if report.recommendations:
            console.print("\n[bold]💡 Recommendations[/bold]")
            console.print("─" * 18)

            for recommendation in report.recommendations[
                :5
            ]:  # Show top 5 recommendations
                console.print(f"  • {recommendation}")

    except ImportError:
        # Fallback to basic output
        print("Code Insight Analyzer v1.0")
        print(f"Project: {report.project_path}")
        print("\n📊 Analysis Summary")
        print("──────────────────")
        print(f"  Total Files:        {report.total_files:,}")
        print(f"  Lines of Code:      {report.total_lines:,}")
        print(f"  Total Size:         {report.total_size:,} bytes")

        if report.language_distribution:
            lang_summary = []
            for lang, count in sorted(
                report.language_distribution.items(), key=lambda x: x[1], reverse=True
            )[:3]:
                percentage = (count / report.total_files) * 100
                lang_summary.append(f"{lang.value} ({percentage:.0f}%)")
            print(f"  Languages:          {', '.join(lang_summary)}")

        # Display top complex files if complexity is enabled
        if show_complexity:
            complex_files = [f for f in report.top_files if f.complexity_metrics]
            if complex_files:
                print("\n🔥 Complexity Hotspots (Top 5)")
                print("────────────────────────────")
                print(
                    "  {:<30} {:<6} {:<10} {:<10}".format(
                        "File", "Lines", "Complexity", "Risk Level"
                    )
                )
                print("  " + "─" * 58)

                for file_insight in complex_files[:5]:
                    complexity = file_insight.complexity_metrics
                    if complexity is not None:
                        cyclomatic = complexity.cyclomatic_complexity

                        # Determine risk level
                        if cyclomatic > 20:
                            risk_level = "🔴 High"
                        elif cyclomatic > 10:
                            risk_level = "🟠 Medium"
                        elif cyclomatic > 5:
                            risk_level = "🟡 Low"
                        else:
                            risk_level = "🟢 Good"

                        print(
                            "  {:<30} {:<6} {:<10.1f} {:<10}".format(
                                str(file_insight.file_metrics.relative_path)[:30],
                                file_insight.file_metrics.lines_of_code,
                                cyclomatic,
                                risk_level,
                            )
                        )
                    else:
                        # Handle case where complexity metrics are not available
                        print(
                            "  {:<30} {:<6} {:<10} {:<10}".format(
                                str(file_insight.file_metrics.relative_path)[:30],
                                file_insight.file_metrics.lines_of_code,
                                "-",
                                "N/A",
                            )
                        )

        print(f"\n📁 Top Files by Line Count (Top {top_files})")
        print("─" * (33 + len(str(top_files))))
        print("  {:<30} {:<6} {:<12}".format("File", "Lines", "Size"))
        print("  " + "─" * 50)

        for file_insight in report.top_files[:top_files]:
            print(
                "  {:<30} {:<6} {:<12}".format(
                    str(file_insight.file_metrics.relative_path)[:30],
                    file_insight.file_metrics.lines_of_code,
                    f"{file_insight.file_metrics.size_bytes:,} bytes",
                )
            )

        # Display code smells if any
        smells_found = []
        for file_insight in report.top_files:
            if file_insight.code_smells:
                smells_found.extend(
                    [
                        (file_insight.file_metrics.relative_path, smell)
                        for smell in file_insight.code_smells
                    ]
                )

        if smells_found:
            print("\n💡 Code Smells Detected")
            print("───────────────────────")
            for file_path, smell in smells_found[:10]:  # Show top 10 smells
                print(f"  • {file_path}: {smell}")

        # Display code duplications if any
        duplications_found = []
        for file_insight in report.top_files:
            if file_insight.duplications:
                for duplication in file_insight.duplications:
                    duplications_found.append(
                        (file_insight.file_metrics.relative_path, duplication)
                    )

        if duplications_found:
            print("\n🔍 Code Duplications Detected")
            print("────────────────────────────")
            for file_path, duplication in duplications_found[
                :10
            ]:  # Show top 10 duplications
                dup_info = f"{duplication.type} '{duplication.name}' ({duplication.count} duplicates)"
                print(f"  • {file_path}: {dup_info}")

        # Display recommendations if any
        if report.recommendations:
            print("\n💡 Recommendations")
            print("─────────────────")
            for recommendation in report.recommendations[
                :5
            ]:  # Show top 5 recommendations
                print(f"  • {recommendation}")


def _export_results(
    report: AnalysisReport, formats: List[str], export_dir: Path
) -> None:
    """Export results to specified formats."""
    export_dir.mkdir(exist_ok=True)

    for fmt in formats:
        try:
            if fmt == "json":
                json_exporter = JSONExporter()
                json_exporter.export(report, export_dir / "report.json")
                typer.echo(f"Exported JSON report to {export_dir / 'report.json'}")
            elif fmt == "csv":
                csv_exporter = CSVExporter()
                csv_exporter.export(report, export_dir / "report.csv")
                typer.echo(f"Exported CSV report to {export_dir / 'report.csv'}")
            elif fmt == "html":
                html_exporter = HTMLExporter()
                html_exporter.export(report, export_dir / "report.html")
                typer.echo(f"Exported HTML report to {export_dir / 'report.html'}")
            else:
                typer.echo(f"Warning: Unknown export format '{fmt}'")
        except Exception as e:
            typer.echo(f"Error exporting to {fmt}: {e}")


@app.command()
def compare(
    report1_path: Path = typer.Argument(..., help="First report file (JSON)"),
    report2_path: Path = typer.Argument(..., help="Second report file (JSON)"),
    output: str = typer.Option(
        "terminal", "--output", "-o", help="Output format (terminal, json)"
    ),
) -> None:
    """Compare two analysis reports."""
    # Load the reports
    try:
        with open(report1_path, "r") as f:
            report1_data = json.load(f)
        report1 = AnalysisReport.from_dict(report1_data)

        with open(report2_path, "r") as f:
            report2_data = json.load(f)
        report2 = AnalysisReport.from_dict(report2_data)
    except Exception as e:
        typer.echo(f"Error loading reports: {e}")
        raise typer.Exit(1)

    # Compare the reports
    comparator = ReportComparator()
    comparison = comparator.compare(report1, report2)

    # Display output based on format
    if output == "terminal":
        _display_comparison_terminal(comparison, report1, report2)
    elif output == "json":
        typer.echo(json.dumps(comparison, indent=2))


def _display_comparison_terminal(
    comparison: Dict[str, Any], report1: AnalysisReport, report2: AnalysisReport
) -> None:
    """Display comparison results in terminal with Rich formatting."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel

        console = Console()

        # Display summary panel
        console.print(
            Panel(
                f"[bold]Code Insight Analysis Comparison[/bold]\n"
                f"Report 1: {report1.project_path} ({report1.timestamp.strftime('%Y-%m-%d %H:%M:%S')})\n"
                f"Report 2: {report2.project_path} ({report2.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"
            )
        )

        # Display summary comparison
        summary = comparison["summary"]
        table = Table(title="Summary Comparison")
        table.add_column("Metric", style="cyan")
        table.add_column("Report 1", justify="right", style="green")
        table.add_column("Report 2", justify="right", style="blue")
        table.add_column("Difference", justify="right", style="yellow")
        table.add_column("Change %", justify="right", style="magenta")

        table.add_row(
            "Total Files",
            str(summary["total_files"]["report1"]),
            str(summary["total_files"]["report2"]),
            f"{summary['total_files']['difference']:+d}",
            f"{summary['total_files']['percentage_change']:+.1f}%",
        )

        table.add_row(
            "Total Lines",
            f"{summary['total_lines']['report1']:,}",
            f"{summary['total_lines']['report2']:,}",
            f"{summary['total_lines']['difference']:+d}",
            f"{summary['total_lines']['percentage_change']:+.1f}%",
        )

        table.add_row(
            "Total Size",
            f"{summary['total_size']['report1']:,}",
            f"{summary['total_size']['report2']:,}",
            f"{summary['total_size']['difference']:+d}",
            f"{summary['total_size']['percentage_change']:+.1f}%",
        )

        console.print(table)

        # Display file changes if any
        files = comparison["files"]
        if files["new_files"] or files["removed_files"] or files["changed_files"]:
            console.print("\n[bold]File Changes:[/bold]")

            if files["new_files"]:
                console.print(f"  [green]+ {len(files['new_files'])} new files[/green]")

            if files["removed_files"]:
                console.print(
                    f"  [red]- {len(files['removed_files'])} removed files[/red]"
                )

            if files["changed_files"]:
                console.print(
                    f"  [yellow]~ {len(files['changed_files'])} changed files[/yellow]"
                )

        # Display complexity changes if any
        complexity = comparison["complexity"]
        if complexity["files_with_changes"]:
            console.print("\n[bold]Complexity Changes:[/bold]")
            console.print(
                f"  {len(complexity['files_with_changes'])} files with complexity changes"
            )

    except ImportError:
        # Fallback to basic output
        print("Code Insight Analysis Comparison")
        print(
            f"Report 1: {report1.project_path} ({report1.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"
        )
        print(
            f"Report 2: {report2.project_path} ({report2.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"
        )

        summary = comparison["summary"]
        print("\nSummary:")
        print(
            f"  Total Files: {summary['total_files']['report1']} -> {summary['total_files']['report2']} "
            f"({summary['total_files']['difference']:+d}, {summary['total_files']['percentage_change']:+.1f}%)"
        )
        print(
            f"  Total Lines: {summary['total_lines']['report1']:,} -> {summary['total_lines']['report2']:,} "
            f"({summary['total_lines']['difference']:+d}, {summary['total_lines']['percentage_change']:+.1f}%)"
        )
        print(
            f"  Total Size: {summary['total_size']['report1']:,} -> {summary['total_size']['report2']:,} "
            f"({summary['total_size']['difference']:+d}, {summary['total_size']['percentage_change']:+.1f}%)"
        )


def _display_live_terminal(
    report: AnalysisReport, show_complexity: bool, top_files: int = 20
) -> None:
    """Display results in terminal with Rich formatting for live updates."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.live import Live

        console = Console()

        # Create the display components
        def create_display():
            # Display main header
            header = Panel(
                f"[bold]Code Insight Analyzer v1.0 (Live)[/bold]\n"
                f"[cyan]Project:[/cyan] {report.project_path}\n"
                f"[yellow]Last Updated:[/yellow] {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                expand=False,
            )

            # Display analysis summary
            summary_text = f"""
[bold]📊 Analysis Summary[/bold]
──────────────────
Total Files:     {report.total_files:,}
Lines of Code:   {report.total_lines:,}
Total Size:      {report.total_size:,} bytes"""

            # Language distribution summary
            if report.language_distribution:
                lang_summary = []
                for lang, count in sorted(
                    report.language_distribution.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:3]:
                    percentage = (count / report.total_files) * 100
                    lang_summary.append(f"{lang.value} ({percentage:.0f}%)")
                summary_text += f"\nLanguages:       {', '.join(lang_summary)}"

            # Display top files by line count
            files_table = Table(show_header=True, title="📁 Top Files by Line Count")
            files_table.add_column("File", style="cyan")
            files_table.add_column("Lines", justify="right", style="green")
            files_table.add_column("Size", justify="right", style="magenta")

            for file_insight in report.top_files[:top_files]:
                files_table.add_row(
                    str(file_insight.file_metrics.relative_path),
                    str(file_insight.file_metrics.lines_of_code),
                    f"{file_insight.file_metrics.size_bytes:,} bytes",
                )

            return header, summary_text, files_table

        # For now, we'll just print the updated report each time
        # In a more advanced implementation, we could use Rich's Live display
        console.clear()
        header, summary_text, files_table = create_display()
        console.print(header)
        console.print(summary_text)
        console.print(files_table)

        # Display complexity if requested
        if show_complexity:
            complex_files = [f for f in report.top_files if f.complexity_metrics]
            if complex_files:
                complexity_table = Table(
                    show_header=True, title="🔥 Complexity Hotspots"
                )
                complexity_table.add_column("File", style="cyan")
                complexity_table.add_column("Lines", justify="right", style="green")
                complexity_table.add_column(
                    "Complexity", justify="right", style="yellow"
                )
                complexity_table.add_column("Risk Level", justify="center")

                for file_insight in complex_files[:5]:
                    complexity = file_insight.complexity_metrics
                    if complexity is not None:
                        cyclomatic = complexity.cyclomatic_complexity

                        # Determine risk level
                        if cyclomatic > 20:
                            risk_level = "[red]🔴 High[/red]"
                        elif cyclomatic > 10:
                            risk_level = "[orange]🟠 Medium[/orange]"
                        elif cyclomatic > 5:
                            risk_level = "[yellow]🟡 Low[/yellow]"
                        else:
                            risk_level = "[green]🟢 Good[/green]"

                        complexity_table.add_row(
                            str(file_insight.file_metrics.relative_path),
                            str(file_insight.file_metrics.lines_of_code),
                            f"{cyclomatic:.1f}",
                            risk_level,
                        )

                console.print(complexity_table)

    except ImportError:
        # Fallback to basic output
        print("\033[2J\033[H")  # Clear screen and move cursor to top-left
        print("Code Insight Analyzer v1.0 (Live)")
        print(f"Project: {report.project_path}")
        print(f"Last Updated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n📊 Analysis Summary")
        print("──────────────────")
        print(f"  Total Files:        {report.total_files:,}")
        print(f"  Lines of Code:      {report.total_lines:,}")
        print(f"  Total Size:         {report.total_size:,} bytes")

        if report.language_distribution:
            lang_summary = []
            for lang, count in sorted(
                report.language_distribution.items(), key=lambda x: x[1], reverse=True
            )[:3]:
                percentage = (count / report.total_files) * 100
                lang_summary.append(f"{lang.value} ({percentage:.0f}%)")
            print(f"  Languages:          {', '.join(lang_summary)}")

        print(f"\n📁 Top Files by Line Count (Top {top_files})")
        print("─" * (33 + len(str(top_files))))
        print("  {:<30} {:<6} {:<12}".format("File", "Lines", "Size"))
        print("  " + "─" * 50)

        for file_insight in report.top_files[:top_files]:
            print(
                "  {:<30} {:<6} {:<12}".format(
                    str(file_insight.file_metrics.relative_path)[:30],
                    file_insight.file_metrics.lines_of_code,
                    f"{file_insight.file_metrics.size_bytes:,} bytes",
                )
            )


@app.command()
def watch(
    path: Path = typer.Argument(..., help="Path to watch"),
    complexity: bool = typer.Option(
        False, "--complexity", "-c", help="Include complexity analysis"
    ),
    top_files: int = typer.Option(
        20, "--top-files", "-t", help="Number of top files to display [default: 20]"
    ),
) -> None:
    """Watch a codebase for changes and display real-time analysis."""
    typer.echo(f"Watching {path} for changes... Press Ctrl+C to stop.")

    # Create watcher
    watcher = CodeWatcher(path)

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        typer.echo("\nStopping watcher...")
        watcher.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Start watching
    try:
        watcher.start(
            analysis_callback=lambda report: _display_live_terminal(
                report, complexity, top_files
            ),
            include_complexity=complexity,
        )

        # Keep the process running
        while True:
            import time

            time.sleep(1)
    except KeyboardInterrupt:
        typer.echo("\nStopping watcher...")
        watcher.stop()


if __name__ == "__main__":
    app()
