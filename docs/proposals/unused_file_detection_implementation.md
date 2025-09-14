# Proposal: Implement Unused File Detection in Refactoroscope

## Overview
This document proposes implementing unused file detection capability in Refactoroscope to identify completely unused files in Python projects. This feature would complement the existing unused code detection by focusing on entire files rather than individual code elements.

## Current State
Refactoroscope currently has:
- Unused code detection for functions, classes, variables, and imports within files
- AST-based analysis approach
- CLI command for unused code detection
- Configuration management system

What's missing is the ability to detect completely unused files - files that are never imported or referenced by any other file in the project.

## Proposed Implementation

### 1. New Analyzer Module
Create a new analyzer module at `src/codeinsight/analyzers/unused_files.py`:

```python
"""
Unused file analyzer for detecting completely unused files
"""

from pathlib import Path
from typing import List, Set, Dict
import ast
import networkx as nx
from codeinsight.models.metrics import Language, UnusedFileFinding
from codeinsight.config.manager import ConfigManager

class UnusedFileAnalyzer:
    """Analyzes Python projects for unused files using dependency graph analysis"""
    
    def analyze(self, project_path: Path, config_manager: ConfigManager) -> List[UnusedFileFinding]:
        """
        Analyze a project for unused files
        
        Args:
            project_path: Root path of the project
            config_manager: Configuration manager for analysis settings
            
        Returns:
            List of unused file findings
        """
        # Only analyze Python projects for now
        if not self._is_python_project(project_path):
            return []
            
        try:
            # Build dependency graph
            graph_builder = FileDependencyGraphBuilder(project_path, config_manager)
            dependency_graph = graph_builder.build_graph()
            
            # Find entry points
            entry_points = graph_builder.find_entry_points()
            
            # Identify unused files
            unused_files = self._find_unused_files(dependency_graph, entry_points)
            
            # Convert to findings with confidence scores
            findings = []
            for unused_file in unused_files:
                confidence = self._calculate_confidence(unused_file, dependency_graph)
                reason = self._generate_reason(unused_file, dependency_graph)
                
                findings.append(UnusedFileFinding(
                    path=unused_file,
                    confidence=confidence,
                    reason=reason
                ))
                
            return findings
        except Exception as e:
            print(f"Warning: Could not analyze unused files for {project_path}: {e}")
            return []

    def _is_python_project(self, project_path: Path) -> bool:
        """Check if this is a Python project"""
        # Look for Python files or common Python project indicators
        return (
            any(project_path.rglob("*.py")) or
            (project_path / "setup.py").exists() or
            (project_path / "pyproject.toml").exists() or
            (project_path / "requirements.txt").exists()
        )

    def _find_unused_files(self, graph: nx.DiGraph, entry_points: List[Path]) -> List[Path]:
        """Find files that are not reachable from entry points"""
        # Find all reachable files
        reachable: Set[Path] = set()
        for entry_point in entry_points:
            if entry_point in graph:
                reachable.add(entry_point)
                # Add all descendants (files that this entry point imports)
                reachable.update(nx.descendants(graph, entry_point))
                
        # Unused files are all files minus reachable files
        all_files = set(graph.nodes())
        unused_files = list(all_files - reachable)
        
        return unused_files

    def _calculate_confidence(self, file_path: Path, graph: nx.DiGraph) -> float:
        """Calculate confidence score for an unused file detection"""
        # Base confidence
        confidence = 0.7
        
        # Adjust based on file characteristics
        file_name = file_path.name
        
        # Files that are commonly entry points but might not be detected
        if file_name in ["main.py", "app.py", "run.py", "cli.py"]:
            confidence -= 0.3
            
        # Test files are often not imported by main code
        if file_name.startswith("test_") or file_name.endswith("_test.py"):
            confidence -= 0.4
            
        # Configuration files
        if file_name in ["setup.py", "conftest.py", "manage.py"]:
            confidence -= 0.2
            
        # Files with __main__ guards are likely entry points
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if '__name__ == "__main__"' in content:
                    confidence -= 0.3
        except Exception:
            pass
            
        return max(0.1, min(0.9, confidence))  # Keep between 0.1 and 0.9

    def _generate_reason(self, file_path: Path, graph: nx.DiGraph) -> str:
        """Generate a reason for why a file is considered unused"""
        # Check if it's imported by any file
        importing_files = []
        for source, target in graph.edges():
            if target == file_path:
                importing_files.append(source)
                
        if not importing_files:
            return "File is never imported by any other file in the project"
        else:
            return f"File is only imported by {len(importing_files)} other unused files"

class FileDependencyGraphBuilder:
    """Builds a dependency graph of files in a Python project"""
    
    def __init__(self, project_path: Path, config_manager: ConfigManager):
        self.project_path = project_path
        self.config_manager = config_manager
        self.graph = nx.DiGraph()
        self.file_modules: Dict[Path, str] = {}
        self.module_files: Dict[str, Path] = {}
        
    def build_graph(self) -> nx.DiGraph:
        """Build the file dependency graph"""
        # Step 1: Initialize nodes
        self._initialize_nodes()
        
        # Step 2: Add edges based on imports
        self._add_import_edges()
        
        return self.graph
        
    def _initialize_nodes(self):
        """Initialize graph nodes for all Python files"""
        for py_file in self.project_path.rglob("*.py"):
            # Skip files that should be ignored
            if self.config_manager.should_ignore_file(py_file):
                continue
                
            try:
                # Map file to module name
                relative_path = py_file.relative_to(self.project_path)
                module_parts = list(relative_path.parts)
                
                if module_parts[-1] == "__init__.py":
                    module_parts = module_parts[:-1]
                else:
                    module_parts[-1] = module_parts[-1][:-3]  # Remove .py
                    
                module_name = ".".join(module_parts)
                
                # Add node with metadata
                self.graph.add_node(py_file, module_name=module_name)
                self.file_modules[py_file] = module_name
                self.module_files[module_name] = py_file
            except (ValueError, OSError):
                continue
                
    def _add_import_edges(self):
        """Add edges based on import statements"""
        for py_file in self.graph.nodes():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    
                # Extract all imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self._add_import_edge(py_file, alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self._add_import_edge(py_file, node.module)
            except Exception:
                # Skip files that can't be parsed
                continue
                
    def _add_import_edge(self, source_file: Path, module_name: str):
        """Add an import edge to the graph"""
        target_file = self._resolve_module(module_name)
        if target_file and target_file != source_file:
            # Add edge
            self.graph.add_edge(source_file, target_file)
            
    def _resolve_module(self, module_name: str) -> Path:
        """Resolve a module name to a file path"""
        # Exact match
        if module_name in self.module_files:
            return self.module_files[module_name]
            
        # Package match (__init__.py)
        package_module = f"{module_name}.__init__"
        if package_module in self.module_files:
            return self.module_files[package_module]
            
        # Partial match for submodules
        for module, file_path in self.module_files.items():
            if module.startswith(f"{module_name}."):
                return file_path
                
        return None
        
    def find_entry_points(self) -> List[Path]:
        """Find entry point files in the project"""
        entry_points: List[Path] = []
        
        # Files with __main__ guard
        for node in self.graph.nodes():
            try:
                with open(node, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '__name__ == "__main__"' in content:
                        entry_points.append(node)
            except Exception:
                continue
                
        # Root-level files and common entry point names
        common_entry_names = ["main.py", "app.py", "run.py", "cli.py", "manage.py"]
        for py_file in self.project_root.glob("*.py"):
            if (py_file in self.graph and 
                (py_file not in entry_points) and 
                (py_file.name in common_entry_names or py_file.parent == self.project_root)):
                entry_points.append(py_file)
                
        return entry_points
```

### 2. Update Data Models
Add the new data model to `src/codeinsight/models/metrics.py`:

```python
@dataclass
class UnusedFileFinding:
    """Represents a completely unused file"""
    
    path: Path
    confidence: float
    reason: str
```

### 3. Integrate with Scanner
Update the scanner to include unused file analysis in `src/codeinsight/scanner.py`:

```python
# Add import
from codeinsight.analyzers.unused_files import UnusedFileAnalyzer

# Add to __init__
def __init__(self, project_path: Optional[Path] = None, enable_duplicates: bool = True, enable_ai: bool = False):
    # ... existing code
    self.unused_file_analyzer = UnusedFileAnalyzer()

# Add to analyze method to collect unused files at project level
def analyze(self, path: Path, include_complexity: bool = False) -> AnalysisReport:
    # ... existing code
    
    # Add unused file analysis at the end
    unused_files = self.unused_file_analyzer.analyze(path, self.config_manager)
    
    # Add unused files to report recommendations
    if unused_files:
        report.recommendations.extend([
            f"Unused file detected: {finding.path} (confidence: {finding.confidence:.0%}) - {finding.reason}"
            for finding in unused_files
        ])
    
    return report
```

### 4. Add CLI Command
Add a new CLI command in `src/codeinsight/cli.py`:

```python
@app.command()
def unused_files(
    path: Path = typer.Argument(..., help="Path to analyze for unused files"),
    entry_points: List[Path] = typer.Option([], "--entry-point", "-e", help="Entry point files to consider"),
    output: str = typer.Option("terminal", "--output", "-o", help="Output format (terminal, json)"),
    confidence_threshold: float = typer.Option(0.5, "--confidence", "-c", help="Confidence threshold (0.0 to 1.0)")
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
            match = re.search(r'confidence: (\d+)%', recommendation)
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
        from rich.table import Table
        from rich.panel import Panel
        
        console = Console()
        
        # Display main header
        console.print(
            Panel(
                f"[bold]Refactoroscope - Unused File Analysis[/bold]\n"
                f"[cyan]Unused files are files that are never imported by any other file in the project.[/cyan]",
                expand=False,
            )
        )
        
        if findings:
            console.print(f"\n[bold]🔍 Unused File Findings ({len(findings)} found)[/bold]")
            console.print("─" * 40)
            
            for finding in findings:
                console.print(f"• {finding}")
        else:
            console.print("[green]✅ No unused files found above the confidence threshold.[/green]")
            
    except ImportError:
        # Fallback to basic output
        print("Refactoroscope - Unused File Analysis")
        print("Unused files are files that are never imported by any other file in the project.")
        
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
        "findings": findings
    }
    
    print(json.dumps(output, indent=2))
```

### 5. Update Configuration
Add configuration options to `.refactoroscope.yml`:

```yaml
analysis:
  unused_files:
    # Enable/disable unused file detection
    enabled: true
    
    # Confidence threshold for reporting (0.0 to 1.0)
    confidence_threshold: 0.5
    
    # Explicitly specify entry points
    entry_points:
      - "main.py"
      - "app.py"
    
    # Patterns to ignore for unused file detection
    ignore_patterns:
      - "test_*.py"
      - "*_test.py"
      - "*/migrations/*"
    
    # Include/exclude specific directories for unused file analysis
    include_dirs:
      - "src/"
    exclude_dirs:
      - "tests/"
      - "docs/"
```

## Dependencies
This implementation would require adding NetworkX as a dependency for graph analysis:

```toml
# In pyproject.toml
dependencies = [
    # ... existing dependencies
    "networkx>=3.1"
]
```

## Benefits
1. **Comprehensive Analysis**: Identifies completely unused files that can be safely removed
2. **Reduced Technical Debt**: Helps clean up codebases by removing dead code
3. **Improved Maintainability**: Smaller, cleaner codebases are easier to maintain
4. **Resource Optimization**: Removing unused files reduces project size and complexity
5. **Integration Consistency**: Follows existing Refactoroscope patterns and architecture

## Implementation Timeline
1. **Week 1**: Implement core analyzer module and data models
2. **Week 2**: Integrate with scanner and add CLI command
3. **Week 3**: Add configuration support and testing
4. **Week 4**: Documentation and user guides

## Testing Strategy
1. **Unit Tests**: Test individual components of the unused file analyzer
2. **Integration Tests**: Test integration with the scanner and CLI
3. **End-to-End Tests**: Test with sample projects that have known unused files
4. **Performance Tests**: Ensure analysis doesn't significantly impact performance

This implementation would provide valuable unused file detection capabilities while maintaining consistency with the existing Refactoroscope architecture.