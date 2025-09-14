"""
Unused code analyzer using AST-based approach
"""

import ast
from pathlib import Path
from typing import Dict, List, Set

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
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
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

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track function definitions"""
        self._add_definition("function", node.name, node.lineno)
        self._enter_scope(node.name)
        self.generic_visit(node)
        self._exit_scope()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track async function definitions"""
        self._add_definition("function", node.name, node.lineno)
        self._enter_scope(node.name)
        self.generic_visit(node)
        self._exit_scope()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track class definitions"""
        self._add_definition("class", node.name, node.lineno)
        self._enter_scope(node.name)
        self.generic_visit(node)
        self._exit_scope()

    def visit_Name(self, node: ast.Name) -> None:
        """Track variable names"""
        if isinstance(node.ctx, ast.Store):
            # Variable assignment
            self._add_definition("variable", node.id, node.lineno)
        elif isinstance(node.ctx, ast.Load):
            # Variable usage
            self.usages.add(node.id)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Track imports"""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self._add_definition("import", name, node.lineno)
            self.imports.append(
                {
                    "name": name,
                    "original": alias.name,
                    "line": node.lineno,
                    "type": "import",
                }
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from imports"""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self._add_definition("import", name, node.lineno)
            self.imports.append(
                {
                    "name": name,
                    "original": alias.name,
                    "module": node.module,
                    "line": node.lineno,
                    "type": "from_import",
                }
            )

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Track attribute usage"""
        if isinstance(node.ctx, ast.Load):
            # Track attribute access
            attr_name = self._get_attribute_name(node)
            if attr_name:
                self.usages.add(attr_name)
        self.generic_visit(node)

    def _add_definition(self, type_: str, name: str, line: int) -> None:
        """Add a definition to tracking"""
        if name not in self.definitions:
            self.definitions[name] = []
        self.definitions[name].append(
            {
                "type": type_,
                "name": name,
                "line": line,
                "scope": ".".join(self.current_scope),
            }
        )

    def _enter_scope(self, name: str) -> None:
        """Enter a new scope"""
        self.current_scope.append(name)

    def _exit_scope(self) -> None:
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

                    findings.append(
                        UnusedCodeFinding(
                            type=definition["type"],
                            name=name,
                            line=definition["line"],
                            confidence=self._calculate_confidence(definition),
                            reason="Defined but never used",
                        )
                    )

        return findings

    def _is_special_name(self, name: str) -> bool:
        """Check if name is a special case that should be ignored"""
        special_names = {
            "__init__",
            "__str__",
            "__repr__",
            "__len__",
            "__iter__",
            "__getitem__",
            "__setitem__",
            "__delitem__",
            "__contains__",
            "__enter__",
            "__exit__",
            "__call__",
            "__getattr__",
            "__setattr__",
            "__eq__",
            "__ne__",
            "__lt__",
            "__le__",
            "__gt__",
            "__ge__",
            "__add__",
            "__sub__",
            "__mul__",
            "__div__",
            "__mod__",
        }
        return name in special_names

    def _calculate_confidence(self, definition: Dict) -> float:
        """Calculate confidence level for a finding"""
        type_confidence = {
            "import": 0.9,
            "function": 0.7,
            "class": 0.7,
            "variable": 0.6,
        }
        return type_confidence.get(definition["type"], 0.5)
