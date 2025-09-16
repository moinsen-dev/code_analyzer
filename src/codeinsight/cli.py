"""
Refactoroscope CLI
"""

import json
import signal
import sys
from pathlib import Path
from typing import Any, Dict, List

# Version information
__version__ = "0.4.0"

import typer

from codeinsight.analysis.comparator import ReportComparator
from codeinsight.exporters.csv_exporter import CSVExporter
from codeinsight.exporters.html_exporter import HTMLExporter
from codeinsight.exporters.json_exporter import JSONExporter
from codeinsight.models.metrics import AnalysisReport
from codeinsight.scanner import Scanner
from codeinsight.watcher import CodeWatcher


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"Refactoroscope CLI Version: {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="refactoroscope",
    help="A comprehensive code analysis tool",
    add_completion=False,
)


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit",
    )
) -> None:
    """
    Refactoroscope CLI - A comprehensive code analysis tool
    """
    pass


@app.command()
def init(
    path: Path = typer.Argument(".", help="Path to initialize configuration"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing configuration file"
    ),
) -> None:
    """Initialize a .refactoroscope.yml configuration file in the project directory."""
    config_path = path / ".refactoroscope.yml"

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

# AI configuration
# AI providers require API keys which should be set as environment variables:
# - OpenAI: OPENAI_API_KEY
# - Anthropic: ANTHROPIC_API_KEY
# - Google: GOOGLE_API_KEY
# - Ollama: No API key required (runs locally)
# - Qwen: No API key required (runs locally)
ai:
  # Enable AI-powered code suggestions
  enable_ai_suggestions: true
  
  # Maximum file size to analyze with AI (in bytes)
  max_file_size: 50000
  
  # Whether to cache AI analysis results
  cache_results: true
  
  # Cache time-to-live in seconds
  cache_ttl: 3600
  
  # Preference order for AI providers
  provider_preferences:
    - "openai"
    - "anthropic"
    - "google"
    - "ollama"
    - "qwen"
  
  # Provider configurations
  providers:
    openai:
      # API key (can also be set via OPENAI_API_KEY environment variable)
      # api_key: "your-openai-api-key"
      
      # Model to use
      model: "gpt-5-mini"
      
      # Whether this provider is enabled
      enabled: true
    
    anthropic:
      # API key (can also be set via ANTHROPIC_API_KEY environment variable)
      # api_key: "your-anthropic-api-key"
      
      # Model to use
      model: "claude-sonnet-4-20250514"
      
      # Whether this provider is enabled
      enabled: true
    
    google:
      # API key (can also be set via GOOGLE_API_KEY environment variable)
      # api_key: "your-google-api-key"
      
      # Model to use
      model: "gemini-2.5-flash"
      
      # Whether this provider is enabled
      enabled: true
    
    ollama:
      # Ollama doesn't require API keys
      
      # Model to use
      model: "qwen3-coder"
      
      # Base URL for Ollama (default is localhost)
      base_url: "http://localhost:11434"
      
      # Whether this provider is enabled
      enabled: true
    
    qwen:
      # Qwen doesn't require API keys for local installations
      
      # Model to use
      model: "qwen"
      
      # Base URL for Qwen (default is localhost)
      base_url: "http://localhost:11434"
      
      # Whether this provider is enabled
      enabled: true

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
        typer.echo(f"Created .refactoroscope.yml configuration file at {config_path}")
    except Exception as e:
        typer.echo(f"Error creating configuration file: {e}")
        raise typer.Exit(1)


@app.command()
def analyze(
    path: Path = typer.Argument(..., help="Path to analyze"),
    complexity: bool = typer.Option(
        True,
        "--complexity/--no-complexity",
        "-c/-C",
        help="Include complexity analysis [default: enabled]",
    ),
    duplicates: bool = typer.Option(
        True,
        "--duplicates/--no-duplicates",
        help="Enable/disable duplicate code detection",
    ),
    ai: bool = typer.Option(
        False,
        "--ai/--no-ai",
        help="Enable/disable AI-powered code suggestions",
    ),
    check: bool = typer.Option(
        False,
        "--check",
        help="Check tech stacks and run appropriate tools for each subfolder",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show verbose output during tech stack analysis",
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

    # If check option is enabled, run tech stack detection and tools
    if check:
        _run_tech_stack_check(path, verbose)
        return

    # Initialize scanner with the project path
    scanner = Scanner(path, enable_duplicates=duplicates, enable_ai=ai)

    # Perform analysis
    report = scanner.analyze(path, include_complexity=complexity)

    # Display output based on format
    if output == "terminal":
        _display_terminal(report, complexity, top_files, duplicates)
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
    report: AnalysisReport,
    show_complexity: bool,
    top_files: int = 20,
    show_duplicates: bool = True,
) -> None:
    """Display results in terminal with Rich formatting."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()

        # Display main header
        console.print(
            Panel(
                f"[bold]Refactoroscope v1.0[/bold]\n"
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
        if show_duplicates:
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
                dup_table.add_column("Type", style="magenta")
                dup_table.add_column("Similarity", style="green")

                for file_path, duplication in duplications_found[
                    :10
                ]:  # Show top 10 duplications
                    dup_info = f"{duplication.type} '{duplication.name}' ({duplication.count} duplicates)"
                    clone_type = duplication.clone_type.capitalize()
                    similarity = f"{duplication.similarity:.2f}"
                    dup_table.add_row(file_path, dup_info, clone_type, similarity)

                console.print(dup_table)

        # Display recommendations if any
        if report.recommendations:
            console.print("\n[bold]💡 Recommendations[/bold]")
            console.print("─" * 18)

            # Create a table for recommendations
            from rich import box

            rec_table = Table(
                box=box.ROUNDED, show_header=True, show_edge=True, padding=(0, 1)
            )
            rec_table.add_column("#", style="dim", width=3)
            rec_table.add_column("Issue", overflow="fold")
            rec_table.add_column("Details", overflow="fold")

            # Add top recommendations to the table
            for i, recommendation in enumerate(
                report.recommendations[:10], 1
            ):  # Show top 10 recommendations
                # Parse recommendation to extract file and details
                if (
                    "Unused file detected:" in recommendation
                    and " - File is never imported" in recommendation
                ):
                    # Split into file path and details
                    parts = recommendation.split(" - File is never imported")
                    file_info = parts[0].replace("Unused file detected: ", "").strip()
                    details = "File is never imported by any other file in the project"
                    if len(parts) > 1:
                        details += parts[1].strip()
                    rec_table.add_row(str(i), file_info, details)
                else:
                    rec_table.add_row(str(i), recommendation, "")

            console.print(rec_table)

    except ImportError:
        # Fallback to basic output
        print("Refactoroscope v1.0")
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
        if show_duplicates:
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
                    print(
                        f"  • {file_path}: {dup_info} [{duplication.clone_type}, {duplication.similarity:.2f}]"
                    )

        # Display recommendations if any
        if report.recommendations:
            print("\n💡 Recommendations")
            print("─────────────────")
            for i, recommendation in enumerate(
                report.recommendations[:10], 1
            ):  # Show top 10 recommendations
                # Simple cleaner display
                print(f"{i}. {recommendation}")


def _run_tech_stack_check(path: Path, verbose: bool = False) -> None:
    """Run tech stack detection and appropriate tools for each subfolder."""
    typer.echo(f"Checking tech stacks in {path}")

    # Import required modules for tech stack detection
    from codeinsight.analysis.tech_stack_detector import TechStackDetector
    from codeinsight.analysis.tech_stack_runner import TechStackRunner

    # Detect tech stacks
    if verbose:
        typer.echo("  → Detecting tech stacks...")
    detector = TechStackDetector()
    tech_stacks = detector.detect_stacks(path)

    # Run appropriate tools for each detected tech stack
    if verbose:
        typer.echo("  → Running tools for detected tech stacks...")
    runner = TechStackRunner()
    results = runner.run_tools_for_stacks(path, tech_stacks, verbose)

    # Display results
    _display_tech_stack_results(results)


def _display_tech_stack_results(results: Dict) -> None:
    """Display tech stack check results in terminal."""
    try:
        from pathlib import Path

        from rich import box
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()

        # Display summary
        console.print(Panel("[bold]Tech Stack Analysis Results[/bold]", expand=False))

        # Display results for each folder
        for folder, folder_results in results.items():
            # Expand relative paths to full paths
            full_path = Path(folder).resolve() if folder == "." else Path.cwd() / folder

            # Create project information table
            info_table = Table(box=box.ROUNDED, show_header=False)
            info_table.add_column("Property", style="bold")
            info_table.add_column("Value")
            info_table.add_row("📁 Folder", str(full_path))

            # Try to get project name from folder or pyproject.toml
            project_name = _get_project_name(full_path)
            if project_name:
                info_table.add_row("📦 Project", project_name)

            # Add AI summary if available (prioritize over basic README summary)
            ai_summary_added = False
            if "ai_summary" in folder_results and folder_results["ai_summary"]:
                ai_summary = folder_results["ai_summary"]
                if "project_overview" in ai_summary and ai_summary["project_overview"]:
                    info_table.add_row("📝 Description", ai_summary["project_overview"])
                    ai_summary_added = True
                # Add tech stack specific summaries
                for key, summary in ai_summary.items():
                    if key != "project_overview" and summary:
                        stack_name = key.replace("_summary", "").title()
                        info_table.add_row(f"🧠 {stack_name} AI", summary)

            # Fallback to basic README summary if no AI summary
            if not ai_summary_added:
                readme_content = _get_readme_summary(full_path)
                if readme_content:
                    info_table.add_row("📝 Description", readme_content)

            console.print(info_table)

            # Display detected tech stacks in a table
            if "tech_stacks" in folder_results and folder_results["tech_stacks"]:
                stacks_table = Table(show_header=False, box=box.SIMPLE, show_edge=False)
                stacks_table.add_column("Stack", style="cyan")
                for stack in folder_results["tech_stacks"]:
                    stacks_table.add_row(f"• {stack}")
                console.print("[bold]🎯 Detected Tech Stacks:[/bold]")
                console.print(stacks_table)

            # Display tool results in a table
            if "tool_results" in folder_results and folder_results["tool_results"]:
                tools_table = Table(box=box.ROUNDED)
                tools_table.add_column("Tool", style="bold")
                tools_table.add_column("Status", style="bold")
                tools_table.add_column("Details", overflow="fold")

                for tool, result in folder_results["tool_results"].items():
                    status = (
                        "[green]✓ Passed[/green]"
                        if result.get("success", False)
                        else "[red]✗ Failed[/red]"
                    )
                    details = (
                        result.get("output", "")[:200] + "..."
                        if len(result.get("output", "")) > 200
                        else result.get("output", "")
                    )
                    tools_table.add_row(tool, status, details)

                console.print("[bold]🔧 Tool Results:[/bold]")
                console.print(tools_table)

            # Display outdated packages in a table
            if (
                "outdated_packages" in folder_results
                and folder_results["outdated_packages"]
            ):
                packages_table = Table(box=box.ROUNDED)
                packages_table.add_column("Package", style="bold")
                packages_table.add_column("Current", style="yellow")
                packages_table.add_column("Latest", style="green")
                packages_table.add_column("Update Available", style="bold")

                for package, version_info in folder_results[
                    "outdated_packages"
                ].items():
                    current = version_info.get("current", "Unknown")
                    latest = version_info.get("latest", "Unknown")
                    packages_table.add_row(
                        package, current, latest, f"[red]{current} → {latest}[/red]"
                    )

                console.print("[bold]📦 Outdated Packages:[/bold]")
                console.print(packages_table)

            console.print("")  # Add spacing between folders

    except ImportError:
        # Fallback to basic print if Rich is not available
        print("Tech Stack Analysis Results:")
        for folder, folder_results in results.items():
            print(f"\nFolder: {folder}")
            if "tech_stacks" in folder_results:
                print("Detected Tech Stacks:")
                for stack in folder_results["tech_stacks"]:
                    print(f"  • {stack}")
            if "tool_results" in folder_results:
                print("Tool Results:")
                for tool, result in folder_results["tool_results"].items():
                    status = "Passed" if result.get("success", False) else "Failed"
                    print(f"  • {tool}: {status}")
            if "outdated_packages" in folder_results:
                print("Outdated Packages:")
                for package, version_info in folder_results[
                    "outdated_packages"
                ].items():
                    print(
                        f"  • {package}: {version_info['current']} -> {version_info['latest']}"
                    )


def _get_readme_summary(folder_path: Path) -> str:
    """Get a summary from README.md file"""
    readme_files = ["README.md", "README.txt", "README"]
    for readme_file in readme_files:
        readme_path = folder_path / readme_file
        if readme_path.exists():
            try:
                with open(readme_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    # Extract first meaningful lines (skip empty lines and headers)
                    lines = [
                        line.strip()
                        for line in content.split("\n")
                        if line.strip() and not line.strip().startswith("#")
                    ]
                    if lines:
                        # Get first 100 characters of the first meaningful line
                        summary = lines[0][:100]
                        if len(lines[0]) > 100:
                            summary += "..."
                        return summary
            except Exception:
                pass
    return ""


def _get_project_name(folder_path: Path) -> str:
    """Get project name from pyproject.toml or folder name"""
    # Try to get from pyproject.toml
    pyproject_path = folder_path / "pyproject.toml"
    if pyproject_path.exists():
        try:
            with open(pyproject_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Simple parsing for project name
                if "name" in content:
                    lines = content.split("\n")
                    for line in lines:
                        if "name" in line and "=" in line:
                            # Extract name value (simple approach)
                            parts = line.split("=")
                            if len(parts) >= 2:
                                name = parts[1].strip().strip('"').strip("'")
                                return name
        except Exception:
            pass

    # Fallback to folder name
    return folder_path.name if folder_path.name else folder_path.parent.name


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
        from rich.panel import Panel
        from rich.table import Table

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
        from rich.panel import Panel
        from rich.table import Table

        console = Console()

        # Create the display components
        def create_display() -> tuple:
            # Display main header
            header = Panel(
                f"[bold]Refactoroscope v1.0 (Live)[/bold]\n"
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
        print("Refactoroscope v1.0 (Live)")
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
def duplicates(
    path: Path = typer.Argument(..., help="Path to analyze for duplicates"),
    clone_type: str = typer.Option(
        "all",
        "--type",
        "-t",
        help="Type of clones to detect (exact, renamed, modified, semantic, all)",
    ),
    min_similarity: float = typer.Option(
        0.7, "--min-similarity", help="Minimum similarity threshold (0.0 to 1.0)"
    ),
    output: str = typer.Option(
        "terminal", "--output", "-o", help="Output format (terminal, json)"
    ),
) -> None:
    """Analyze codebase for duplicate code patterns"""
    typer.echo(f"Analyzing {path} for duplicate code...")

    # Initialize scanner with duplicate detection enabled
    scanner = Scanner(path, enable_duplicates=True)

    # Perform analysis
    report = scanner.analyze(path, include_complexity=True)

    # Display output based on format
    if output == "terminal":
        _display_duplicates_terminal(report, clone_type, min_similarity)
    elif output == "json":
        typer.echo(report.json())


def _display_duplicates_terminal(
    report: AnalysisReport, clone_type_filter: str = "all", min_similarity: float = 0.7
) -> None:
    """Display duplicate code findings in terminal"""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()

        # Display main header
        console.print(
            Panel(
                f"[bold]Refactoroscope - Duplicate Code Analysis[/bold]\n"
                f"[cyan]Project:[/cyan] {report.project_path}",
                expand=False,
            )
        )

        # Collect all duplications
        all_duplications = []
        for file_insight in report.top_files:
            if file_insight.duplications:
                for duplication in file_insight.duplications:
                    # Apply filters
                    if (
                        clone_type_filter != "all"
                        and duplication.clone_type != clone_type_filter
                    ):
                        continue
                    if duplication.similarity < min_similarity:
                        continue
                    all_duplications.append(
                        (file_insight.file_metrics.relative_path, duplication)
                    )

        # Sort by similarity (descending)
        all_duplications.sort(key=lambda x: x[1].similarity, reverse=True)

        if all_duplications:
            console.print(
                f"\n[bold]🔍 Duplicate Code Findings ({len(all_duplications)} found)[/bold]"
            )
            console.print("─" * 40)

            dup_table = Table(show_header=True)
            dup_table.add_column("File", style="cyan")
            dup_table.add_column("Type", style="magenta")
            dup_table.add_column("Name", style="yellow")
            dup_table.add_column("Count", justify="right", style="green")
            dup_table.add_column("Similarity", justify="right", style="blue")

            for file_path, duplication in all_duplications[:20]:  # Show top 20
                dup_table.add_row(
                    file_path,
                    duplication.clone_type.capitalize(),
                    f"{duplication.type} '{duplication.name}'",
                    str(duplication.count),
                    f"{duplication.similarity:.2f}",
                )

            console.print(dup_table)

            # Show detailed locations for top duplications
            console.print("\n[bold]📍 Detailed Locations (Top 5)[/bold]")
            console.print("─" * 30)

            for i, (file_path, duplication) in enumerate(all_duplications[:5]):
                console.print(
                    f"\n[bold]{i+1}. {duplication.type} '{duplication.name}'[/bold]"
                )
                console.print(f"   Clone Type: {duplication.clone_type.capitalize()}")
                console.print(f"   Similarity: {duplication.similarity:.2f}")
                console.print("   Locations:")
                for location in duplication.locations[:5]:  # Show first 5 locations
                    loc_file = location.get("file", file_path)
                    loc_line = location.get("line", "Unknown")
                    console.print(f"     • {loc_file}:{loc_line}")

        else:
            console.print(
                "[green]✅ No duplicate code found matching the criteria.[/green]"
            )

    except ImportError:
        # Fallback to basic output
        print("Refactoroscope - Duplicate Code Analysis")
        print(f"Project: {report.project_path}")

        # Collect all duplications
        all_duplications = []
        for file_insight in report.top_files:
            if file_insight.duplications:
                for duplication in file_insight.duplications:
                    # Apply filters
                    if (
                        clone_type_filter != "all"
                        and duplication.clone_type != clone_type_filter
                    ):
                        continue
                    if duplication.similarity < min_similarity:
                        continue
                    all_duplications.append(
                        (file_insight.file_metrics.relative_path, duplication)
                    )

        # Sort by similarity (descending)
        all_duplications.sort(key=lambda x: x[1].similarity, reverse=True)

        if all_duplications:
            print(f"\n🔍 Duplicate Code Findings ({len(all_duplications)} found)")
            print("────────────────────────────────────────")

            for file_path, duplication in all_duplications[:20]:  # Show top 20
                print(
                    f"  {file_path}: {duplication.type} '{duplication.name}' "
                    f"({duplication.count} duplicates) "
                    f"[{duplication.clone_type}, {duplication.similarity:.2f}]"
                )

            # Show detailed locations for top duplications
            print("\n📍 Detailed Locations (Top 5)")
            print("──────────────────────────────")

            for i, (file_path, duplication) in enumerate(all_duplications[:5]):
                print(f"\n{i+1}. {duplication.type} '{duplication.name}'")
                print(f"   Clone Type: {duplication.clone_type.capitalize()}")
                print(f"   Similarity: {duplication.similarity:.2f}")
                print("   Locations:")
                for location in duplication.locations[:5]:  # Show first 5 locations
                    loc_file = location.get("file", file_path)
                    loc_line = location.get("line", "Unknown")
                    print(f"     • {loc_file}:{loc_line}")
        else:
            print("✅ No duplicate code found matching the criteria.")


@app.command()
def watch(
    path: Path = typer.Argument(..., help="Path to watch"),
    complexity: bool = typer.Option(
        True,
        "--complexity/--no-complexity",
        "-c/-C",
        help="Include complexity analysis [default: enabled]",
    ),
    ai: bool = typer.Option(
        False,
        "--ai/--no-ai",
        help="Enable/disable AI-powered code suggestions",
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
    def signal_handler(sig: int, frame) -> None:  # type: ignore
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
            enable_ai=ai,
        )

        # Keep the process running
        while True:
            import time

            time.sleep(1)
    except KeyboardInterrupt:
        typer.echo("\nStopping watcher...")
        watcher.stop()


@app.command()
def unused_files(
    path: Path = typer.Argument(..., help="Path to analyze for unused files"),
    entry_points: List[Path] = typer.Option(
        [], "--entry-point", "-e", help="Entry point files to consider"
    ),
    output: str = typer.Option(
        "terminal", "--output", "-o", help="Output format (terminal, json)"
    ),
    confidence_threshold: float = typer.Option(
        0.5, "--confidence", "-c", help="Confidence threshold (0.0 to 1.0)"
    ),
) -> None:
    """Analyze codebase for completely unused files"""
    typer.echo(f"Analyzing {path} for unused files...")

    # Initialize scanner
    scanner = Scanner(path, enable_duplicates=False)

    # Perform analysis
    report = scanner.analyze(path, include_complexity=False)

    # Filter unused file findings based on confidence threshold
    unused_file_findings = []
    for recommendation in report.recommendations:
        if "Unused file detected:" in recommendation:
            # Extract confidence from recommendation
            import re

            match = re.search(r"confidence: (\d+)%", recommendation)
            if match:
                confidence = int(match.group(1)) / 100
                if confidence >= confidence_threshold:
                    unused_file_findings.append(recommendation)

    # Display output based on format
    if output == "terminal":
        _display_unused_files_terminal(unused_file_findings)
    elif output == "json":
        _display_unused_files_json(unused_file_findings)


def _display_unused_files_terminal(findings: List[str]) -> None:
    """Display unused file findings in terminal"""
    try:
        from rich.console import Console
        from rich.panel import Panel

        console = Console()

        # Display main header
        console.print(
            Panel(
                "[bold]Refactoroscope - Unused File Analysis[/bold]\n"
                "[cyan]Unused files are files that are never imported by any other file in the project.[/cyan]",
                expand=False,
            )
        )

        if findings:
            console.print(
                f"\n[bold]🔍 Unused File Findings ({len(findings)} found)[/bold]"
            )
            console.print("─" * 40)

            for finding in findings:
                console.print(f"• {finding}")
        else:
            console.print(
                "[green]✅ No unused files found above the confidence threshold.[/green]"
            )

    except ImportError:
        # Fallback to basic output
        print("Refactoroscope - Unused File Analysis")
        print(
            "Unused files are files that are never imported by any other file in the project."
        )

        if findings:
            print(f"\n🔍 Unused File Findings ({len(findings)} found)")
            print("────────────────────────────────────────")

            for finding in findings:
                print(f"• {finding}")
        else:
            print("✅ No unused files found above the confidence threshold.")


def _display_unused_files_json(findings: List[str]) -> None:
    """Display unused file findings as JSON"""
    import json
    from datetime import datetime

    output = {
        "timestamp": datetime.now().isoformat(),
        "unused_files_count": len(findings),
        "findings": findings,
    }

    print(json.dumps(output, indent=2))


@app.command()
def unused(
    path: Path = typer.Argument(..., help="Path to analyze for unused code"),
    output: str = typer.Option(
        "terminal", "--output", "-o", help="Output format (terminal, json)"
    ),
) -> None:
    """Analyze codebase for unused code elements"""
    typer.echo(f"Analyzing {path} for unused code...")

    # Initialize scanner with unused code detection enabled
    scanner = Scanner(path, enable_duplicates=False)

    # Perform analysis
    report = scanner.analyze(path, include_complexity=False)

    # Display output based on format
    if output == "terminal":
        _display_unused_terminal(report)
    elif output == "json":
        typer.echo(report.json())


def _display_unused_terminal(report: AnalysisReport) -> None:
    """Display unused code findings in terminal"""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        console = Console()

        # Display main header
        console.print(
            Panel(
                f"[bold]Refactoroscope - Unused Code Analysis[/bold]\n"
                f"[cyan]Project:[/cyan] {report.project_path}",
                expand=False,
            )
        )

        # Collect all unused code findings
        all_unused = []
        for file_insight in report.top_files:
            if file_insight.unused_code:
                for finding in file_insight.unused_code:
                    all_unused.append(
                        (file_insight.file_metrics.relative_path, finding)
                    )

        if all_unused:
            console.print(
                f"\n[bold]🔍 Unused Code Findings ({len(all_unused)} found)[/bold]"
            )
            console.print("─" * 40)

            unused_table = Table(show_header=True)
            unused_table.add_column("File", style="cyan")
            unused_table.add_column("Type", style="magenta")
            unused_table.add_column("Name", style="yellow")
            unused_table.add_column("Line", justify="right", style="green")
            unused_table.add_column("Confidence", justify="right", style="blue")

            for file_path, finding in all_unused[:50]:  # Show top 50
                confidence_str = f"{finding.confidence:.0%}"
                unused_table.add_row(
                    file_path,
                    finding.type.capitalize(),
                    finding.name,
                    str(finding.line),
                    confidence_str,
                )

            console.print(unused_table)
        else:
            console.print("[green]✅ No unused code found.[/green]")

    except ImportError:
        # Fallback to basic output
        print("Refactoroscope - Unused Code Analysis")
        print(f"Project: {report.project_path}")

        # Collect all unused code findings
        all_unused = []
        for file_insight in report.top_files:
            if file_insight.unused_code:
                for finding in file_insight.unused_code:
                    all_unused.append(
                        (file_insight.file_metrics.relative_path, finding)
                    )

        if all_unused:
            print(f"\n🔍 Unused Code Findings ({len(all_unused)} found)")
            print("────────────────────────────────────────")

            for file_path, finding in all_unused[:50]:  # Show top 50
                confidence_str = f"{finding.confidence:.0%}"
                print(
                    f"  {file_path}: {finding.type} '{finding.name}' "
                    f"(line {finding.line}) [{confidence_str}]"
                )
        else:
            print("✅ No unused code found.")


@app.command()
def refactor_plan(
    path: Path = typer.Argument(
        ..., help="Path to analyze and generate refactoring plan for"
    ),
    provider: str = typer.Option(
        "openai",
        "--provider",
        "-p",
        help="AI provider to use (openai, anthropic, google, ollama, qwen)",
    ),
    output: Path = typer.Option(
        "refactor_plan.md",
        "--output",
        "-o",
        help="Output file for the refactoring plan",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show verbose output including AI prompts and responses",
    ),
) -> None:
    """Generate an AI-based refactoring plan for the codebase."""
    # Import required modules
    from codeinsight.ai.factory import AIProviderFactory
    from codeinsight.analysis.refactor_plan_generator import RefactorPlanGenerator
    from codeinsight.config.manager import ConfigManager

    typer.echo("🔍 Initializing AI provider...")

    # Load configuration
    config_manager = ConfigManager()

    # Check if AI provider is available
    try:
        # Convert string provider to enum
        from codeinsight.ai.base import AIProviderType

        try:
            provider_enum = AIProviderType(provider.lower())
        except ValueError:
            typer.echo(
                f"Error: Unknown AI provider '{provider}'. Valid options are: openai, anthropic, google, ollama, qwen"
            )
            raise typer.Exit(1)

        ai_provider = AIProviderFactory.get_provider_instance(
            provider_enum, config_manager
        )
        if not ai_provider.is_available():
            typer.echo(
                f"Error: AI provider '{provider}' is not available or not configured properly."
            )
            typer.echo("Please check your configuration and API keys.")
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: Could not initialize AI provider '{provider}': {e}")
        raise typer.Exit(1)

    typer.echo("✅ AI provider initialized successfully")
    typer.echo("📊 Analyzing codebase... (this may take a moment)")

    # Generate refactoring plan
    generator = RefactorPlanGenerator(ai_provider)
    plan = generator.generate_plan(path, verbose=verbose)

    typer.echo("🤖 Generating refactoring plan with AI...")

    # Save plan to file
    try:
        with open(output, "w") as f:
            f.write(plan)
        typer.echo(f"✅ Refactoring plan saved to {output}")
    except Exception as e:
        typer.echo(f"Error saving refactoring plan: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
