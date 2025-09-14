"""
Code smell detection functionality
"""

import ast
from pathlib import Path
from typing import Any, Dict, List

from codeinsight.models.metrics import Duplication, Language


class CodeSmellDetector:
    """Detects common code smells in source code"""

    def detect_smells(self, file_path: Path, language: Language) -> List[str]:
        """
        Detect code smells in a file

        Args:
            file_path: Path to the file
            language: Language of the file

        Returns:
            List of detected code smells
        """
        # Only analyze Python files for now
        if language != Language.PYTHON:
            return []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Parse the AST
            tree = ast.parse(content)

            # Detect various code smells
            smells = []
            smells.extend(self._detect_long_methods(tree))
            smells.extend(self._detect_large_classes(tree))
            smells.extend(self._detect_complex_conditionals(tree))
            smells.extend(self._detect_long_parameter_lists(tree))
            smells.extend(self._detect_nested_blocks(tree))

            return smells

        except Exception as e:
            print(f"Warning: Could not detect code smells for {file_path}: {e}")
            return []

    def _detect_long_methods(self, tree: ast.AST) -> List[str]:
        """Detect methods that are too long"""
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count statements in the function
                statement_count = 0
                for child in ast.walk(node):
                    if isinstance(child, (ast.stmt,)) and not isinstance(
                        child, (ast.FunctionDef, ast.ClassDef)
                    ):
                        statement_count += 1

                if statement_count > 20:  # Threshold for long methods
                    smells.append(
                        f"Long method '{node.name}' with {statement_count} statements"
                    )

        return smells

    def _detect_large_classes(self, tree: ast.AST) -> List[str]:
        """Detect classes that are too large"""
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Count methods and attributes in the class
                method_count = 0
                attr_count = 0

                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        method_count += 1
                    elif isinstance(child, ast.Assign):
                        attr_count += len(child.targets)

                total_members = method_count + attr_count
                if total_members > 10:  # Threshold for large classes
                    smells.append(
                        f"Large class '{node.name}' with {total_members} members"
                    )

        return smells

    def _detect_complex_conditionals(self, tree: ast.AST) -> List[str]:
        """Detect conditionals with too many conditions"""
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # Count conditions in the if statement
                condition_count = self._count_conditions(node.test)
                if condition_count > 3:  # Threshold for complex conditionals
                    smells.append(
                        f"Complex conditional with {condition_count} conditions"
                    )

        return smells

    def _count_conditions(self, node: ast.AST) -> int:
        """Count the number of conditions in a boolean expression"""
        if isinstance(node, ast.BoolOp):
            # Count operands in boolean operations
            count = 0
            for value in node.values:
                count += self._count_conditions(value)
            return count
        elif isinstance(node, (ast.Compare, ast.Call, ast.Name, ast.Constant)):
            # Simple conditions count as 1
            return 1
        else:
            # Recursively count for other node types
            count = 0
            for child in ast.iter_child_nodes(node):
                count += self._count_conditions(child)
            return count

    def _detect_duplicate_code(self, content: str) -> List[str]:
        """Detect duplicate code blocks using AST-based approach"""
        try:
            # Parse the AST
            tree = ast.parse(content)

            # Extract code blocks and their hashes
            code_blocks = self._extract_code_blocks(tree)

            # Find duplicate blocks
            duplicates = self._find_duplicate_blocks(code_blocks)

            # Return formatted duplicate reports
            smells = []
            for block_hash, locations in duplicates.items():
                if len(locations) > 1:  # Found duplicates
                    # Get the first few lines of the duplicate block for context
                    first_location = locations[0]
                    smells.append(
                        f"Found {len(locations)} duplicate code blocks (first at line {first_location['line']})"
                    )

            return smells
        except Exception:
            # Fallback to simple line-based detection if AST parsing fails
            lines = content.splitlines()

            # Look for consecutive duplicate lines
            duplicate_count = 0
            for i in range(len(lines) - 1):
                if lines[i].strip() and lines[i].strip() == lines[i + 1].strip():
                    duplicate_count += 1
                else:
                    if duplicate_count > 2:  # Threshold for duplicate code
                        return [
                            f"Found {duplicate_count + 1} consecutive duplicate lines"
                        ]
                    duplicate_count = 0

            if duplicate_count > 2:
                return [f"Found {duplicate_count + 1} consecutive duplicate lines"]

            return []

    def _extract_code_blocks(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract code blocks from AST with their structural information"""
        blocks = []

        # Walk the AST to find function and class definitions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Extract function body as a block
                block_info = {
                    "type": "function",
                    "name": node.name,
                    "line": node.lineno,
                    "hash": self._hash_ast_node(node),
                    "node": node,
                }
                blocks.append(block_info)
            elif isinstance(node, ast.ClassDef):
                # Extract class body as a block
                block_info = {
                    "type": "class",
                    "name": node.name,
                    "line": node.lineno,
                    "hash": self._hash_ast_node(node),
                    "node": node,
                }
                blocks.append(block_info)
            elif isinstance(node, (ast.For, ast.While, ast.If)):
                # Extract control structures as blocks
                block_info = {
                    "type": type(node).__name__.lower(),
                    "name": f"{type(node).__name__.lower()}_block",
                    "line": getattr(node, "lineno", 0),
                    "hash": self._hash_ast_node(node),
                    "node": node,
                }
                blocks.append(block_info)

        return blocks

    def _hash_ast_node(self, node: ast.AST) -> str:
        """Create a structural hash of an AST node"""
        # Convert node to string representation and hash it
        # This is a simplified approach - a more sophisticated implementation
        # would normalize the AST before hashing
        try:
            # Get the node type and key attributes
            node_info = []
            node_info.append(type(node).__name__)

            # Add key attributes that affect structure
            if hasattr(node, "name"):
                node_info.append(f"name:{node.name}")
            if hasattr(node, "args") and hasattr(node.args, "args"):
                node_info.append(f"params:{len(node.args.args)}")
            if hasattr(node, "body"):
                node_info.append(
                    f"body:{len(node.body) if isinstance(node.body, list) else 1}"
                )

            # Create hash from structural info
            import hashlib

            structural_info = "|".join(node_info)
            return hashlib.md5(
                structural_info.encode(), usedforsecurity=False
            ).hexdigest()
        except Exception:
            # Fallback to simple hash
            return str(hash(str(type(node))))

    def _find_duplicate_blocks(
        self, blocks: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Find duplicate code blocks by their hashes"""
        duplicates: Dict[str, List[Dict[str, Any]]] = {}

        # Group blocks by hash
        for block in blocks:
            block_hash = block["hash"]
            if block_hash not in duplicates:
                duplicates[block_hash] = []
            duplicates[block_hash].append(block)

        # Filter to only include hashes with multiple occurrences
        duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}

        return duplicates

    def _detect_long_parameter_lists(self, tree: ast.AST) -> List[str]:
        """Detect functions with too many parameters"""
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                param_count = len(node.args.args)
                if param_count > 5:  # Threshold for long parameter lists
                    smells.append(
                        f"Function '{node.name}' with {param_count} parameters"
                    )

        return smells

    def _detect_nested_blocks(self, tree: ast.AST) -> List[str]:
        """Detect deeply nested blocks"""
        smells = []

        def check_nesting(node: ast.AST, depth: int = 0) -> None:
            if depth > 4:  # Threshold for deep nesting
                if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    smells.append(f"Deeply nested block (depth {depth})")

            # Recursively check child nodes
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                    check_nesting(child, depth + 1)
                else:
                    check_nesting(child, depth)

        check_nesting(tree)
        return smells

    def detect_duplications(
        self, file_path: Path, language: Language
    ) -> List[Duplication]:
        """
        Detect code duplications in a file

        Args:
            file_path: Path to the file
            language: Language of the file

        Returns:
            List of detected duplications
        """
        # Only analyze Python files for now
        if language != Language.PYTHON:
            return []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Parse the AST
            tree = ast.parse(content)

            # Extract code blocks and find duplicates
            code_blocks = self._extract_code_blocks(tree)
            duplicates = self._find_duplicate_blocks(code_blocks)

            # Convert to Duplication objects
            duplications: List[Duplication] = []
            for block_hash, locations in duplicates.items():
                if len(locations) > 1:  # Found duplicates
                    duplication = Duplication(
                        type=locations[0]["type"],
                        name=locations[0]["name"],
                        line=locations[0]["line"],
                        count=len(locations),
                        locations=[
                            {"line": loc["line"], "name": loc["name"]}
                            for loc in locations
                        ],
                    )
                    duplications.append(duplication)

            return duplications

        except Exception as e:
            print(f"Warning: Could not detect duplications for {file_path}: {e}")
            return []
