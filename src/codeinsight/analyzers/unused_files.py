"""
Unused file analyzer for detecting completely unused files
"""

import ast
from pathlib import Path
from typing import Dict, List, Optional, Set

import networkx as nx

from codeinsight.config.manager import ConfigManager
from codeinsight.models.metrics import UnusedFileFinding


class UnusedFileAnalyzer:
    """Analyzes Python projects for unused files using dependency graph analysis"""

    def analyze(
        self, project_path: Path, config_manager: ConfigManager
    ) -> List[UnusedFileFinding]:
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

                findings.append(
                    UnusedFileFinding(
                        path=unused_file, confidence=confidence, reason=reason
                    )
                )

            return findings
        except Exception as e:
            print(f"Warning: Could not analyze unused files for {project_path}: {e}")
            return []

    def _is_python_project(self, project_path: Path) -> bool:
        """Check if this is a Python project"""
        # Look for Python files or common Python project indicators
        return (
            any(project_path.rglob("*.py"))
            or (project_path / "setup.py").exists()
            or (project_path / "pyproject.toml").exists()
            or (project_path / "requirements.txt").exists()
        )

    def _find_unused_files(
        self, graph: nx.DiGraph, entry_points: List[Path]
    ) -> List[Path]:
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
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if '__name__ == "__main__"' in content:
                        confidence -= 0.3
            except Exception:
                pass  # Acceptable as we're just adjusting confidence scores

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
        self.graph: nx.DiGraph = nx.DiGraph()
        self.file_modules: Dict[Path, str] = {}
        self.module_files: Dict[str, Path] = {}

    def build_graph(self) -> nx.DiGraph:
        """Build the file dependency graph"""
        # Step 1: Initialize nodes
        self._initialize_nodes()

        # Step 2: Add edges based on imports
        self._add_import_edges()

        return self.graph

    def _initialize_nodes(self) -> None:
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

    def _add_import_edges(self) -> None:
        """Add edges based on import statements"""
        for py_file in self.graph.nodes():
            try:
                with open(py_file, "r", encoding="utf-8") as f:
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
                continue  # Acceptable as we're processing many files

    def _add_import_edge(self, source_file: Path, module_name: str) -> None:
        """Add an import edge to the graph"""
        target_file = self._resolve_module(module_name)
        if target_file and target_file != source_file:
            # Add edge
            self.graph.add_edge(source_file, target_file)

    def _resolve_module(self, module_name: str) -> Optional[Path]:
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
                with open(node, "r", encoding="utf-8") as f:
                    content = f.read()
                    if '__name__ == "__main__"' in content:
                        entry_points.append(node)
            except Exception:
                continue  # Acceptable as we're checking many files

        # Root-level files and common entry point names
        common_entry_names = ["main.py", "app.py", "run.py", "cli.py", "manage.py"]
        try:
            for py_file in self.project_path.glob("*.py"):
                if (
                    py_file in self.graph
                    and (py_file not in entry_points)
                    and (py_file.name in common_entry_names)
                ):
                    entry_points.append(py_file)
        except Exception:
            pass  # Acceptable as we're just finding additional entry points

        return entry_points
