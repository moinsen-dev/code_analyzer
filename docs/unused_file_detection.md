# Detecting Completely Unused Files in a Codebase

This document outlines various approaches for detecting completely unused files in a codebase, with a focus on practical implementation strategies that could work within the Refactoroscope architecture, particularly for Python projects.

## 1. Static Analysis Approaches Using Import/Require Tracking

### Overview
Static analysis for unused file detection involves tracking import/require statements across all files in a project to build a dependency graph. Files that are never imported or required by any other file are considered unused.

### Implementation Strategy

1. **AST Parsing**: Parse all Python files in the project using the `ast` module
2. **Import Extraction**: Extract all import statements from each file
3. **Reference Tracking**: Track which files import which modules
4. **Reachability Analysis**: Determine which files are reachable from entry points

### Example Implementation Pattern
```python
import ast
from pathlib import Path
from typing import Dict, Set, List

class ImportTracker(ast.NodeVisitor):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.imports: Set[str] = set()
        
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)

class FileDependencyAnalyzer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.file_imports: Dict[Path, Set[str]] = {}
        self.module_paths: Dict[str, Path] = {}
        
    def analyze_project(self) -> List[Path]:
        # Step 1: Discover all Python files and map module names to paths
        self._map_modules()
        
        # Step 2: Extract imports from all files
        self._extract_imports()
        
        # Step 3: Determine which files are imported
        imported_files = self._find_imported_files()
        
        # Step 4: Identify unused files
        all_files = set(self.file_imports.keys())
        unused_files = all_files - imported_files
        
        return list(unused_files)
        
    def _map_modules(self):
        """Map module names to file paths"""
        for py_file in self.project_root.rglob("*.py"):
            # Convert file path to module name
            try:
                relative_path = py_file.relative_to(self.project_root)
                module_name = str(relative_path.with_suffix("")).replace("/", ".").replace("\\", ".")
                if module_name.endswith(".__init__"):
                    module_name = module_name[:-9]  # Remove .__init__
                self.module_paths[module_name] = py_file
            except ValueError:
                continue
                
    def _extract_imports(self):
        """Extract imports from all Python files"""
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    
                tracker = ImportTracker(py_file)
                tracker.visit(tree)
                self.file_imports[py_file] = tracker.imports
            except Exception:
                # Skip files that can't be parsed
                continue
                
    def _find_imported_files(self) -> Set[Path]:
        """Find all files that are imported by other files"""
        imported_files: Set[Path] = set()
        
        for file_path, imports in self.file_imports.items():
            for module_name in imports:
                # Resolve module to file path
                if module_name in self.module_paths:
                    imported_files.add(self.module_paths[module_name])
                    
        return imported_files
```

### Advantages
- Fast execution without running code
- Safe analysis that doesn't require dependencies
- Can analyze large codebases efficiently

### Limitations
- May miss dynamically imported files
- False positives with scripts that are run directly
- Limited understanding of runtime behavior

## 2. Cross-File Dependency Analysis

### Overview
Cross-file dependency analysis extends import tracking to create a complete dependency graph of the entire project, enabling more sophisticated analysis of file relationships.

### Implementation Strategy

1. **Project-Wide Analysis**: Analyze all files together to build a complete picture
2. **Dependency Graph Construction**: Build a graph representing file dependencies
3. **Reachability Analysis**: Use graph algorithms to find unreachable files
4. **Entry Point Identification**: Identify which files are legitimate entry points

### Example Implementation Pattern
```python
import ast
import networkx as nx
from pathlib import Path
from typing import Dict, Set, List

class CrossFileDependencyAnalyzer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dependency_graph = nx.DiGraph()
        self.file_modules: Dict[Path, str] = {}
        self.module_files: Dict[str, Path] = {}
        
    def analyze(self, entry_points: List[Path] = None) -> Dict[str, List[Path]]:
        """
        Analyze project dependencies and identify unused files
        
        Returns:
            Dictionary with keys: 'unused', 'reachable', 'entry_points'
        """
        # Step 1: Map files to module names
        self._map_file_modules()
        
        # Step 2: Build dependency graph
        self._build_dependency_graph()
        
        # Step 3: Identify entry points
        actual_entry_points = self._identify_entry_points(entry_points)
        
        # Step 4: Find reachable files
        reachable_files = self._find_reachable_files(actual_entry_points)
        
        # Step 5: Identify unused files
        all_files = set(self.file_modules.keys())
        unused_files = list(all_files - reachable_files)
        
        return {
            'unused': unused_files,
            'reachable': list(reachable_files),
            'entry_points': actual_entry_points
        }
        
    def _map_file_modules(self):
        """Map each Python file to its module name"""
        for py_file in self.project_root.rglob("*.py"):
            try:
                relative_path = py_file.relative_to(self.project_root)
                module_parts = list(relative_path.parts)
                
                # Handle __init__.py files
                if module_parts[-1] == "__init__.py":
                    module_parts = module_parts[:-1]
                else:
                    module_parts[-1] = module_parts[-1][:-3]  # Remove .py extension
                    
                module_name = ".".join(module_parts)
                self.file_modules[py_file] = module_name
                self.module_files[module_name] = py_file
                self.dependency_graph.add_node(py_file)
            except ValueError:
                continue
                
    def _build_dependency_graph(self):
        """Build dependency graph from import statements"""
        for py_file in self.file_modules.keys():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    
                # Extract imports
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self._add_dependency(py_file, alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self._add_dependency(py_file, node.module)
            except Exception:
                continue
                
    def _add_dependency(self, source_file: Path, module_name: str):
        """Add a dependency edge to the graph"""
        # Resolve module to file
        target_file = self._resolve_module_to_file(module_name)
        if target_file and target_file != source_file:
            self.dependency_graph.add_edge(source_file, target_file)
            
    def _resolve_module_to_file(self, module_name: str) -> Path:
        """Resolve a module name to its file path"""
        # Direct match
        if module_name in self.module_files:
            return self.module_files[module_name]
            
        # Try with __init__.py
        init_module = f"{module_name}.__init__"
        if init_module in self.module_files:
            return self.module_files[init_module]
            
        # Try partial matches for submodules
        for module, file_path in self.module_files.items():
            if module.startswith(f"{module_name}."):
                return file_path
                
        return None
        
    def _identify_entry_points(self, provided_entry_points: List[Path] = None) -> List[Path]:
        """Identify entry point files"""
        if provided_entry_points:
            return provided_entry_points
            
        entry_points = []
        
        # Files with if __name__ == "__main__" patterns
        for py_file in self.file_modules.keys():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '__name__ == "__main__"' in content or "__name__ == '__main__'" in content:
                        entry_points.append(py_file)
            except Exception:
                continue
                
        # Files in common entry point locations
        common_entry_patterns = [
            "main.py",
            "app.py",
            "run.py",
            "start.py",
            "cli.py",
            "manage.py"
        ]
        
        for pattern in common_entry_patterns:
            for py_file in self.project_root.rglob(pattern):
                if py_file not in entry_points:
                    entry_points.append(py_file)
                    
        # Root level Python files (often entry points)
        for py_file in self.project_root.glob("*.py"):
            if py_file not in entry_points:
                entry_points.append(py_file)
                
        return entry_points
        
    def _find_reachable_files(self, entry_points: List[Path]) -> Set[Path]:
        """Find all files reachable from entry points"""
        reachable = set()
        
        for entry_point in entry_points:
            if entry_point in self.dependency_graph:
                # Find all nodes reachable from this entry point
                descendants = nx.descendants(self.dependency_graph, entry_point)
                reachable.add(entry_point)
                reachable.update(descendants)
                
        return reachable
```

### Advantages
- Comprehensive project-wide view
- Can identify completely unused modules
- Good for refactoring guidance
- Handles complex dependency relationships

### Limitations
- Computationally expensive for large codebases
- Requires understanding of project structure
- May require configuration for entry points

## 3. Entry Point Identification

### Overview
Identifying entry points is crucial for determining which files should be considered "reachable" in a dependency analysis. Entry points are files that are intended to be run directly rather than imported.

### Implementation Strategies

1. **Pattern-Based Detection**: Look for common entry point patterns
2. **Configuration-Based Identification**: Use project configuration files
3. **Manual Specification**: Allow users to specify entry points
4. **Framework-Specific Detection**: Recognize framework conventions

### Example Implementation Pattern
```python
import ast
from pathlib import Path
from typing import List, Set

class EntryPointDetector:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def find_entry_points(self) -> List[Path]:
        """Find all entry point files in the project"""
        entry_points: Set[Path] = set()
        
        # 1. Pattern-based detection
        entry_points.update(self._find_pattern_based_entry_points())
        
        # 2. Configuration-based detection
        entry_points.update(self._find_config_entry_points())
        
        # 3. Framework-specific detection
        entry_points.update(self._find_framework_entry_points())
        
        # 4. Root-level Python files (often entry points)
        entry_points.update(self._find_root_py_files())
        
        return list(entry_points)
        
    def _find_pattern_based_entry_points(self) -> Set[Path]:
        """Find entry points based on code patterns"""
        entry_points: Set[Path] = set()
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for main guard pattern
                if ('if __name__ == "__main__"' in content or 
                    "__name__ == '__main__'" in content):
                    entry_points.add(py_file)
                    
                # Look for app.run() or similar patterns
                if "app.run(" in content or "main(" in content:
                    entry_points.add(py_file)
                    
            except Exception:
                continue
                
        return entry_points
        
    def _find_config_entry_points(self) -> Set[Path]:
        """Find entry points from configuration files"""
        entry_points: Set[Path] = set()
        
        # Check setup.py/pyproject.toml for scripts
        setup_files = [
            self.project_root / "setup.py",
            self.project_root / "setup.cfg",
            self.project_root / "pyproject.toml"
        ]
        
        for setup_file in setup_files:
            if setup_file.exists():
                entry_points.update(self._parse_setup_file(setup_file))
                
        # Check package.json for Node.js projects
        package_json = self.project_root / "package.json"
        if package_json.exists():
            entry_points.update(self._parse_package_json(package_json))
            
        return entry_points
        
    def _find_framework_entry_points(self) -> Set[Path]:
        """Find entry points based on framework conventions"""
        entry_points: Set[Path] = set()
        
        # Django projects
        for manage_py in self.project_root.rglob("manage.py"):
            entry_points.add(manage_py)
            
        # Flask projects often have app.py
        for app_py in self.project_root.rglob("app.py"):
            entry_points.add(app_py)
            
        # FastAPI projects
        for main_py in self.project_root.rglob("main.py"):
            entry_points.add(main_py)
            
        return entry_points
        
    def _find_root_py_files(self) -> Set[Path]:
        """Find Python files in the root directory"""
        root_py_files: Set[Path] = set()
        
        for py_file in self.project_root.glob("*.py"):
            root_py_files.add(py_file)
            
        return root_py_files
        
    def _parse_setup_file(self, setup_file: Path) -> Set[Path]:
        """Parse setup files to find entry points"""
        # This is a simplified example
        entry_points: Set[Path] = set()
        return entry_points
        
    def _parse_package_json(self, package_json: Path) -> Set[Path]:
        """Parse package.json to find entry points"""
        # This is a simplified example
        entry_points: Set[Path] = set()
        return entry_points
```

### Advantages
- Reduces false positives by identifying legitimate entry points
- Handles various project types and frameworks
- Improves accuracy of unused file detection

### Limitations
- May miss entry points that don't follow common patterns
- Requires understanding of different frameworks
- Can be complex to implement comprehensively

## 4. File Reference Graph Construction

### Overview
A file reference graph is a directed graph where nodes represent files and edges represent dependencies (imports/uses). Building this graph enables sophisticated analysis of file relationships.

### Implementation Strategy

1. **Node Creation**: Each file becomes a node in the graph
2. **Edge Creation**: Each import creates a directed edge
3. **Graph Analysis**: Use graph algorithms to analyze reachability
4. **Visualization**: Optionally provide visual representations

### Example Implementation Pattern
```python
import ast
import networkx as nx
from pathlib import Path
from typing import Dict, List, Set
import json

class FileReferenceGraph:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.graph = nx.DiGraph()
        self.file_modules: Dict[Path, str] = {}
        self.module_files: Dict[str, Path] = {}
        
    def build_graph(self) -> nx.DiGraph:
        """Build the file reference graph"""
        # Step 1: Initialize nodes
        self._initialize_nodes()
        
        # Step 2: Add edges based on imports
        self._add_import_edges()
        
        # Step 3: Add edges for string references (optional)
        self._add_string_reference_edges()
        
        return self.graph
        
    def _initialize_nodes(self):
        """Initialize graph nodes for all Python files"""
        for py_file in self.project_root.rglob("*.py"):
            try:
                # Map file to module name
                relative_path = py_file.relative_to(self.project_root)
                module_parts = list(relative_path.parts)
                
                if module_parts[-1] == "__init__.py":
                    module_parts = module_parts[:-1]
                else:
                    module_parts[-1] = module_parts[-1][:-3]  # Remove .py
                    
                module_name = ".".join(module_parts)
                
                # Add node with metadata
                self.graph.add_node(
                    py_file,
                    module_name=module_name,
                    file_size=py_file.stat().st_size,
                    last_modified=py_file.stat().st_mtime
                )
                
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
            # Add edge with metadata
            self.graph.add_edge(
                source_file,
                target_file,
                import_type="module",
                module_name=module_name
            )
            
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
        
    def _add_string_reference_edges(self):
        """Add edges based on string references to modules"""
        # This is more complex and can lead to false positives
        # Implementation would involve scanning string literals
        # for potential module references
        pass
        
    def find_unused_files(self, entry_points: List[Path] = None) -> List[Path]:
        """Find files that are not reachable from entry points"""
        if entry_points is None:
            # Auto-detect entry points
            entry_points = self._auto_detect_entry_points()
            
        # Find all reachable files
        reachable: Set[Path] = set()
        for entry_point in entry_points:
            if entry_point in self.graph:
                reachable.add(entry_point)
                # Add all descendants (files that this entry point imports)
                reachable.update(nx.descendants(self.graph, entry_point))
                
        # Unused files are all files minus reachable files
        all_files = set(self.graph.nodes())
        unused_files = list(all_files - reachable)
        
        return unused_files
        
    def _auto_detect_entry_points(self) -> List[Path]:
        """Auto-detect entry points in the project"""
        entry_points: List[Path] = []
        
        # Files with __main__ guard
        for node in self.graph.nodes():
            try:
                with open(node, 'r', encoding='utf-8') as f:
                    if '__name__ == "__main__"' in f.read():
                        entry_points.append(node)
            except Exception:
                continue
                
        # Root-level files
        for py_file in self.project_root.glob("*.py"):
            if py_file in self.graph and py_file not in entry_points:
                entry_points.append(py_file)
                
        return entry_points
        
    def get_statistics(self) -> Dict:
        """Get statistics about the graph"""
        return {
            "total_files": self.graph.number_of_nodes(),
            "total_dependencies": self.graph.number_of_edges(),
            "connected_components": nx.number_weakly_connected_components(self.graph),
            "isolated_files": len(list(nx.isolates(self.graph))),
            "entry_points": len(self._auto_detect_entry_points())
        }
        
    def export_graph(self, format: str = "json") -> str:
        """Export the graph in various formats"""
        if format == "json":
            # Convert graph to JSON-serializable format
            data = {
                "nodes": [],
                "edges": [],
                "metadata": self.get_statistics()
            }
            
            # Add nodes
            for node in self.graph.nodes(data=True):
                node_data = {
                    "path": str(node[0]),
                    "module": node[1].get("module_name", ""),
                    "size": node[1].get("file_size", 0)
                }
                data["nodes"].append(node_data)
                
            # Add edges
            for edge in self.graph.edges(data=True):
                edge_data = {
                    "source": str(edge[0]),
                    "target": str(edge[1]),
                    "type": edge[2].get("import_type", "unknown")
                }
                data["edges"].append(edge_data)
                
            return json.dumps(data, indent=2)
            
        # Other formats could be implemented here
        return ""
```

### Advantages
- Enables sophisticated graph-based analysis
- Provides rich metadata about file relationships
- Can be extended with additional analysis techniques
- Supports visualization and export

### Limitations
- Memory intensive for large projects
- Complex to implement correctly
- May require external libraries (like NetworkX)

## 5. Third-Party Tools That Could Be Integrated

### Popular Tools

#### Vulture
- **Methodology**: AST-based analysis with name tracking
- **Strengths**: Detects unused code with confidence levels, identifies unreachable code
- **Integration Approach**: Parse Vulture's output or use its analysis engine
- **Limitations**: Primarily focuses on code elements rather than entire files

#### Pyflakes
- **Methodology**: AST-based symbol tracking with scope analysis
- **Strengths**: Fast, safe (doesn't execute code), good at finding unused imports
- **Integration Approach**: Leverage pyflakes' robust AST analysis
- **Limitations**: Limited to syntactic analysis, doesn't identify unused files directly

#### Unimport
- **Methodology**: Specialized import analysis
- **Strengths**: Accurate detection of unused imports and star imports
- **Integration Approach**: Focus on import-related analysis
- **Limitations**: Specialized for imports, doesn't handle unused files directly

#### Bandit
- **Methodology**: Security-focused AST analysis
- **Integration Approach**: Could be extended for unused code detection
- **Limitations**: Not designed for unused code detection

### Integration Strategy

1. **Wrapper Approach**: Create wrappers around existing tools
2. **Library Integration**: Directly use tool libraries when available
3. **Output Parsing**: Parse and standardize output from external tools
4. **Hybrid Analysis**: Combine multiple tools for comprehensive coverage

### Example Integration Pattern
```python
import subprocess
import json
from pathlib import Path
from typing import List, Dict

class ThirdPartyToolIntegrator:
    """Integrate third-party tools for unused file detection"""
    
    @staticmethod
    def run_vulture(project_path: Path) -> List[Dict]:
        """Run Vulture and parse its output"""
        try:
            # Run vulture with JSON output
            result = subprocess.run([
                "vulture",
                str(project_path),
                "--json"
            ], capture_output=True, text=True, cwd=project_path)
            
            if result.returncode in [0, 1]:  # Vulture returns 1 for findings
                findings = json.loads(result.stdout)
                return findings
            else:
                print(f"Vulture error: {result.stderr}")
                return []
        except Exception as e:
            print(f"Failed to run Vulture: {e}")
            return []
            
    @staticmethod
    def run_pyflakes(project_path: Path) -> List[str]:
        """Run Pyflakes and parse its output"""
        findings = []
        try:
            # Run pyflakes on all Python files
            for py_file in project_path.rglob("*.py"):
                result = subprocess.run([
                    "pyflakes",
                    str(py_file)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:  # Pyflakes found issues
                    findings.extend(result.stdout.strip().split('\n'))
        except Exception as e:
            print(f"Failed to run Pyflakes: {e}")
            
        return findings
        
    @staticmethod
    def run_unimport(project_path: Path) -> List[str]:
        """Run Unimport and parse its output"""
        try:
            result = subprocess.run([
                "unimport",
                "--check",
                "--diff",
                str(project_path)
            ], capture_output=True, text=True, cwd=project_path)
            
            if result.returncode in [0, 1]:
                return result.stdout.strip().split('\n')
            else:
                print(f"Unimport error: {result.stderr}")
                return []
        except Exception as e:
            print(f"Failed to run Unimport: {e}")
            return []
```

## 6. Best Practices for Accuracy vs. False Positives

### Accuracy Enhancement Techniques

1. **Context-Aware Analysis**: Consider symbol context when determining usage
2. **Entry Point Specification**: Allow users to specify project entry points
3. **Configuration Support**: Provide configuration for ignoring specific patterns
4. **Whitelist Support**: Allow users to whitelist known false positives
5. **Framework Awareness**: Understand common framework patterns and conventions

### False Positive Reduction Techniques

1. **Confidence Scoring**: Assign confidence levels to findings
2. **Pattern Recognition**: Identify common false positive patterns
3. **User Feedback Loop**: Allow users to mark findings as valid/invalid
4. **Multiple Analysis Passes**: Cross-validate findings with different techniques
5. **Incremental Analysis**: Track changes over time to reduce noise

### Example Confidence Scoring System
```python
class ConfidenceScorer:
    """Assign confidence scores to unused file detections"""
    
    def __init__(self):
        # Base confidence scores for different file types
        self.file_type_confidence = {
            "__init__.py": 0.3,  # Often empty but important
            "test_*.py": 0.2,    # Test files may not be imported by main code
            "*_test.py": 0.2,
            "conftest.py": 0.1,  # Pytest configuration files
            "setup.py": 0.9,     # Usually an entry point
            "main.py": 0.9,
            "app.py": 0.8,
            "manage.py": 0.9,    # Django entry point
        }
        
        # Confidence adjustments based on file characteristics
        self.characteristics_adjustments = {
            "has_main_guard": 0.3,      # Files with if __name__ == "__main__":
            "has_shebang": 0.2,         # Executable scripts
            "in_scripts_dir": 0.3,      # Files in scripts/ directory
            "has_cli_imports": 0.2,     # Imports from CLI frameworks
            "recently_modified": -0.1,  # Recently modified files
        }
        
    def score_unused_file(self, file_path: Path, context: Dict) -> float:
        """Calculate confidence score for an unused file detection"""
        base_score = 0.7  # Default confidence
        
        # Adjust based on file name patterns
        file_name = file_path.name
        for pattern, adjustment in self.file_type_confidence.items():
            if "*" in pattern:
                import fnmatch
                if fnmatch.fnmatch(file_name, pattern):
                    base_score += adjustment
            elif file_name == pattern:
                base_score += adjustment
                
        # Adjust based on file characteristics
        for characteristic, adjustment in self.characteristics_adjustments.items():
            if context.get(characteristic, False):
                base_score += adjustment
                
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, base_score))
        
    def should_report(self, file_path: Path, context: Dict, threshold: float = 0.5) -> bool:
        """Determine if an unused file should be reported based on confidence"""
        confidence = self.score_unused_file(file_path, context)
        return confidence >= threshold
```

## Integration with Refactoroscope Architecture

### Implementation Approach

1. **Analyzer Module**: Create a new analyzer following the existing pattern
2. **Model Integration**: Add unused file findings to the existing data models
3. **CLI Command**: Add a new CLI command for unused file analysis
4. **Configuration**: Add configuration options for unused file detection

### Proposed Implementation Steps

1. **Create Analyzer Module**:
   ```python
   # src/codeinsight/analyzers/unused_files.py
   class UnusedFileAnalyzer:
       def analyze(self, project_path: Path, config: ConfigManager) -> List[UnusedFileFinding]:
           # Implementation for unused file detection
           pass
   ```

2. **Update Models**:
   ```python
   # src/codeinsight/models/metrics.py
   @dataclass
   class UnusedFileFinding:
       """Represents a completely unused file"""
       path: Path
       confidence: float
       reason: str
       references: List[str]  # What would need to import this file
   ```

3. **Integrate with Scanner**:
   ```python
   # src/codeinsight/scanner.py
   def _analyze_file_parallel(self, file_path: Path, root_path: Path, include_complexity: bool):
       # ... existing code
       # Add unused file analysis at project level
   ```

4. **Add CLI Command**:
   ```python
   # src/codeinsight/cli.py
   @app.command()
   def unused_files(
       path: Path = typer.Argument(..., help="Path to analyze"),
       entry_points: List[Path] = typer.Option([], "--entry-point", help="Entry point files")
   ):
       # Implementation for unused file detection
       pass
   ```

### Configuration Options

```yaml
# .refactoroscope.yml
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
      - "scripts/"
    
    # Patterns to ignore (in addition to global ignore patterns)
    ignore_patterns:
      - "test_*.py"
      - "*/migrations/*"
      - "*/fixtures/*"
    
    # Include/exclude specific directories
    include_dirs:
      - "src/"
    exclude_dirs:
      - "tests/"
      - "docs/"
      
    # Integration with third-party tools
    third_party_tools:
      vulture: true
      pyflakes: true
      unimport: true
```

This approach would maintain consistency with the existing Refactoroscope architecture while adding comprehensive unused file detection capabilities.