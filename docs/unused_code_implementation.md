# Implementation Plan: Unused Code Detection for Refactoroscope

This document outlines a detailed implementation plan for adding unused code detection capabilities to Refactoroscope, following the existing architectural patterns.

## 1. Module Structure

Based on the existing Refactoroscope architecture, we'll create a new analyzer module:

```
src/codeinsight/analyzers/
├── __init__.py
├── complexity.py
├── line_counter.py
└── unused_code.py  # New module
```

## 2. Data Model Updates

We need to extend the existing data models to accommodate unused code findings:

```python
# src/codeinsight/models/metrics.py

@dataclass
class UnusedCodeFinding:
    """Represents a single unused code finding"""
    type: str  # function, class, variable, import, etc.
    name: str  # Name of the unused element
    line: int  # Line number where it's defined
    confidence: float  # Confidence level (0.0 to 1.0)
    reason: str  # Explanation of why it's considered unused

@dataclass
class CodeInsights:
    # ... existing fields
    unused_code: List[UnusedCodeFinding] = field(default_factory=list)
```

## 3. Analyzer Implementation

### Core Analyzer Class

```python
# src/codeinsight/analyzers/unused_code.py

from pathlib import Path
from typing import List, Set, Dict, Tuple
import ast
from codeinsight.models.metrics import Language, UnusedCodeFinding

class UnusedCodeAnalyzer:
    """Analyzes Python code for unused elements using AST-based approach"""
    
    def analyze(self, file_path: Path, language: Language) -> List[UnusedCodeFinding]:
        """
        Analyze a file for unused code elements
        
        Args:
            file_path: Path to the file to analyze
            language: Language of the file
            
        Returns:
            List of unused code findings
        """
        if language != Language.PYTHON:
            return []
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            tree = ast.parse(content)
            visitor = UnusedCodeVisitor(file_path)
            visitor.visit(tree)
            
            return visitor.get_unused_findings()
        except Exception as e:
            print(f"Warning: Could not analyze unused code for {file_path}: {e}")
            return []

class UnusedCodeVisitor(ast.NodeVisitor):
    """AST visitor that tracks definitions and usages to find unused code"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.definitions: Dict[str, List[Dict]] = {}  # name -> [{type, line, ...}]
        self.usages: Set[str] = set()
        self.imports: List[Dict] = []
        self.current_scope: List[str] = []  # Stack of scope names
        
    def visit_FunctionDef(self, node):
        """Track function definitions"""
        self._add_definition('function', node.name, node.lineno)
        self._enter_scope(node.name)
        self.generic_visit(node)
        self._exit_scope()
        
    def visit_ClassDef(self, node):
        """Track class definitions"""
        self._add_definition('class', node.name, node.lineno)
        self._enter_scope(node.name)
        self.generic_visit(node)
        self._exit_scope()
        
    def visit_Name(self, node):
        """Track variable names"""
        if isinstance(node.ctx, ast.Store):
            # Variable assignment
            self._add_definition('variable', node.id, node.lineno)
        elif isinstance(node.ctx, ast.Load):
            # Variable usage
            self.usages.add(node.id)
        self.generic_visit(node)
        
    def visit_Import(self, node):
        """Track imports"""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self._add_definition('import', name, node.lineno)
            self.imports.append({
                'name': name,
                'original': alias.name,
                'line': node.lineno,
                'type': 'import'
            })
            
    def visit_ImportFrom(self, node):
        """Track from imports"""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self._add_definition('import', name, node.lineno)
            self.imports.append({
                'name': name,
                'original': alias.name,
                'module': node.module,
                'line': node.lineno,
                'type': 'from_import'
            })
            
    def visit_Attribute(self, node):
        """Track attribute usage"""
        if isinstance(node.ctx, ast.Load):
            # Track attribute access
            attr_name = self._get_attribute_name(node)
            if attr_name:
                self.usages.add(attr_name)
        self.generic_visit(node)
        
    def _add_definition(self, type_: str, name: str, line: int):
        """Add a definition to tracking"""
        if name not in self.definitions:
            self.definitions[name] = []
        self.definitions[name].append({
            'type': type_,
            'name': name,
            'line': line,
            'scope': '.'.join(self.current_scope)
        })
        
    def _enter_scope(self, name: str):
        """Enter a new scope"""
        self.current_scope.append(name)
        
    def _exit_scope(self):
        """Exit current scope"""
        if self.current_scope:
            self.current_scope.pop()
            
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Extract full attribute name"""
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node.value, ast.Attribute):
            parent = self._get_attribute_name(node.value)
            if parent:
                return f"{parent}.{node.attr}"
        return node.attr
        
    def get_unused_findings(self) -> List[UnusedCodeFinding]:
        """Get list of unused code findings"""
        findings = []
        
        # Check for unused definitions
        for name, definitions in self.definitions.items():
            if name not in self.usages:
                for definition in definitions:
                    # Skip some special cases that are commonly used
                    if self._is_special_name(name):
                        continue
                        
                    findings.append(UnusedCodeFinding(
                        type=definition['type'],
                        name=name,
                        line=definition['line'],
                        confidence=self._calculate_confidence(definition),
                        reason=f"Defined but never used"
                    ))
                    
        return findings
        
    def _is_special_name(self, name: str) -> bool:
        """Check if name is a special case that should be ignored"""
        special_names = {
            '__init__', '__str__', '__repr__', '__len__', '__iter__',
            '__getitem__', '__setitem__', '__delitem__', '__contains__',
            '__enter__', '__exit__', '__call__', '__getattr__', '__setattr__'
        }
        return name in special_names
        
    def _calculate_confidence(self, definition: Dict) -> float:
        """Calculate confidence level for a finding"""
        type_confidence = {
            'import': 0.9,
            'function': 0.7,
            'class': 0.7,
            'variable': 0.6
        }
        return type_confidence.get(definition['type'], 0.5)
```

## 4. Integration with Scanner

Update the scanner to use the new analyzer:

```python
# src/codeinsight/scanner.py

# Add import
from codeinsight.analyzers.unused_code import UnusedCodeAnalyzer

class Scanner:
    def __init__(self, project_path: Optional[Path] = None, enable_duplicates: bool = True):
        # ... existing initialization
        self.unused_code_analyzer = UnusedCodeAnalyzer()
        
    def _analyze_file_parallel(
        self, file_path: Path, root_path: Path, include_complexity: bool
    ) -> tuple[CodeInsights, FileMetrics] | None:
        # ... existing code
        
        # Add unused code analysis
        unused_code = self.unused_code_analyzer.analyze(file_path, file_metrics.language)
        if unused_code:
            insight.unused_code = unused_code
            
        return (insight, file_metrics)
```

## 5. CLI Integration

Add a new command to the CLI:

```python
# src/codeinsight/cli.py

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
        from rich.table import Table
        from rich.panel import Panel
        
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
            console.print(f"\n[bold]🔍 Unused Code Findings ({len(all_unused)} found)[/bold]")
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
```

## 6. Configuration Options

Add configuration options to `.refactoroscope.yml`:

```yaml
# .refactoroscope.yml

analysis:
  # ... existing configuration
  unused_code:
    enabled: true
    ignore_patterns:
      - "__*__"  # Ignore special methods
      - "test_*"  # Ignore test functions
      - "*_test"  # Ignore test files
    confidence_threshold: 0.6  # Only report findings with this confidence or higher
```

## 7. Testing Strategy

1. **Unit Tests**: Test the analyzer with various code patterns
2. **Integration Tests**: Test end-to-end functionality
3. **False Positive Testing**: Verify common false positive scenarios
4. **Performance Testing**: Ensure analysis doesn't significantly slow down the tool

## 8. Implementation Steps

1. Create the `UnusedCodeAnalyzer` class
2. Update data models with `UnusedCodeFinding` and `unused_code` field
3. Integrate analyzer with the `Scanner` class
4. Add CLI command for unused code analysis
5. Add configuration support
6. Write comprehensive tests
7. Document the new feature
8. Add to README and user documentation

This implementation follows the existing Refactoroscope patterns and provides a solid foundation for unused code detection while maintaining the tool's performance and usability.