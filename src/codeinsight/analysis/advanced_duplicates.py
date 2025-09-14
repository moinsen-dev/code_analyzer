"""
Advanced AST-based duplicate code detection
"""

import ast
import hashlib
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from codeinsight.models.metrics import Duplication, Language


class CloneType(Enum):
    """Types of code clones"""

    EXACT = "exact"  # Type-1: Identical except comments/whitespace
    RENAMED = "renamed"  # Type-2: Syntactically identical with identifier renames
    MODIFIED = "modified"  # Type-3: Semantically similar with small modifications
    SEMANTIC = "semantic"  # Type-4: Semantically equivalent but syntactically different


@dataclass
class NormalizedAST:
    """Normalized AST representation for comparison"""

    normalized_source: str
    identifiers: Set[str]
    literals: Set[str]
    structure_hash: str


class ASTNormalizer:
    """Normalizes ASTs for duplicate detection"""

    def normalize_ast(
        self, tree: ast.AST, language: Language = Language.PYTHON
    ) -> NormalizedAST:
        """
        Normalize an AST by standardizing identifiers and literals

        Args:
            tree: AST to normalize
            language: Programming language

        Returns:
            NormalizedAST with standardized representation
        """
        # Create a copy of the tree to avoid modifying the original
        normalized_tree = ast.parse(ast.unparse(tree))

        # Standardize identifiers
        identifier_mapping: Dict[str, str] = {}
        literal_mapping: Dict[str, str] = {}

        self._normalize_identifiers(normalized_tree, identifier_mapping)
        self._normalize_literals(normalized_tree, literal_mapping)

        # Convert back to source code
        normalized_source = ast.unparse(normalized_tree)

        # Create structure hash
        structure_hash = self._create_structure_hash(normalized_tree)

        return NormalizedAST(
            normalized_source=normalized_source,
            identifiers=set(identifier_mapping.keys()),
            literals=set(literal_mapping.keys()),
            structure_hash=structure_hash,
        )

    def calculate_similarity(self, tree1: ast.AST, tree2: ast.AST) -> float:
        """
        Calculate similarity between two ASTs using multiple metrics

        Args:
            tree1: First AST
            tree2: Second AST

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Normalize both trees
        norm1 = self.normalize_ast(tree1)
        norm2 = self.normalize_ast(tree2)

        # Calculate structure similarity
        structure_similarity = self._calculate_structure_similarity(tree1, tree2)

        # Calculate identifier overlap
        identifier_similarity = self._calculate_identifier_similarity(
            norm1.identifiers, norm2.identifiers
        )

        # Calculate literal overlap
        literal_similarity = self._calculate_literal_similarity(
            norm1.literals, norm2.literals
        )

        # Weighted combination of similarities
        return (
            structure_similarity * 0.7
            + identifier_similarity * 0.2
            + literal_similarity * 0.1
        )

    def _normalize_identifiers(self, node: ast.AST, mapping: Dict[str, str]) -> None:
        """Normalize identifiers in the AST"""
        counter: int = 1

        for n in ast.walk(node):
            # Handle variable names
            if isinstance(n, ast.Name):
                if n.id not in mapping:
                    mapping[n.id] = f"var_{counter}"
                    counter += 1
                n.id = mapping[n.id]

            # Handle function/class names in definitions
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if n.name not in mapping:
                    mapping[n.name] = f"{n.__class__.__name__.lower()}_{counter}"
                    counter += 1
                n.name = mapping[n.name]

            # Handle function arguments
            elif isinstance(n, ast.arg):
                if n.arg not in mapping:
                    mapping[n.arg] = f"param_{counter}"
                    counter += 1
                n.arg = mapping[n.arg]

    def _normalize_literals(self, node: ast.AST, mapping: Dict[str, str]) -> None:
        """Normalize literals in the AST"""
        counter: int = 1

        for n in ast.walk(node):
            # Handle string literals
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                key = f"str_{hash(n.value)}"
                if key not in mapping:
                    mapping[key] = f"LITERAL_STRING_{counter}"
                    counter += 1
                # We don't actually replace the value to preserve functionality
                # but we track it for similarity analysis

            # Handle numeric literals
            elif isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
                key = f"num_{hash(n.value)}"
                if key not in mapping:
                    mapping[key] = f"LITERAL_NUMBER_{counter}"
                    counter += 1
                # We don't actually replace the value to preserve functionality
                # but we track it for similarity analysis

    def _create_structure_hash(self, tree: ast.AST) -> str:
        """Create a hash representing the structural elements of the AST"""
        # Extract structural information
        structural_elements = []

        for node in ast.walk(tree):
            # Add node type
            structural_elements.append(type(node).__name__)

            # Add key attributes that affect structure
            if hasattr(node, "name"):
                structural_elements.append(f"name:{type(node).__name__}")
            if hasattr(node, "args") and hasattr(node.args, "args"):
                structural_elements.append(f"params:{len(node.args.args)}")
            if hasattr(node, "body"):
                structural_elements.append(
                    f"body:{len(node.body) if isinstance(node.body, list) else 1}"
                )

        # Create hash from structural elements
        structural_info = "|".join(sorted(structural_elements))
        return hashlib.md5(structural_info.encode(), usedforsecurity=False).hexdigest()

    def _calculate_structure_similarity(self, tree1: ast.AST, tree2: ast.AST) -> float:
        """Calculate similarity based on structural elements"""
        elements1 = set()
        elements2 = set()

        # Extract elements from both trees
        for node in ast.walk(tree1):
            elements1.add(f"{type(node).__name__}:{getattr(node, 'lineno', 0)}")

        for node in ast.walk(tree2):
            elements2.add(f"{type(node).__name__}:{getattr(node, 'lineno', 0)}")

        # Calculate Jaccard similarity
        intersection = len(elements1.intersection(elements2))
        union = len(elements1.union(elements2))

        return intersection / union if union > 0 else 0.0

    def _calculate_identifier_similarity(self, ids1: Set[str], ids2: Set[str]) -> float:
        """Calculate similarity based on identifier overlap"""
        if not ids1 and not ids2:
            return 1.0
        if not ids1 or not ids2:
            return 0.0

        intersection = len(ids1.intersection(ids2))
        union = len(ids1.union(ids2))

        return intersection / union if union > 0 else 0.0

    def _calculate_literal_similarity(
        self, literals1: Set[str], literals2: Set[str]
    ) -> float:
        """Calculate similarity based on literal overlap"""
        if not literals1 and not literals2:
            return 1.0
        if not literals1 or not literals2:
            return 0.0

        intersection = len(literals1.intersection(literals2))
        union = len(literals1.union(literals2))

        return intersection / union if union > 0 else 0.0


class AdvancedDuplicateDetector:
    """Advanced duplicate code detection using AST normalization"""

    def __init__(self) -> None:
        self.normalizer = ASTNormalizer()
        self._global_index: Dict[str, List[Dict[str, Any]]] = {}
        self._file_cache: Dict[Path, List[Dict[str, Any]]] = {}
        self._file_timestamps: Dict[Path, float] = {}
        self._result_cache: Dict[str, Tuple[float, List[Duplication]]] = {}
        self._cache_ttl = 300  # 5 minutes cache TTL

    def detect_duplicates(
        self, file_path: Path, language: Language
    ) -> List[Duplication]:
        """
        Detect advanced duplicates in a file using AST normalization

        Args:
            file_path: Path to the file to analyze
            language: Language of the file

        Returns:
            List of detected duplications with clone type classification
        """
        # Check if we have cached results
        cache_key = f"{file_path}:{language.value}"
        current_time = time.time()

        # Check cache
        if cache_key in self._result_cache:
            cache_time, cached_results = self._result_cache[cache_key]
            # Check if file has been modified since cache
            try:
                file_mtime = file_path.stat().st_mtime
                if (
                    current_time - cache_time < self._cache_ttl
                    and file_mtime <= cache_time
                ):
                    return cached_results
            except OSError:
                # If we can't stat the file, use cached results
                if current_time - cache_time < self._cache_ttl:
                    return cached_results

        # Only analyze Python files for now
        if language != Language.PYTHON:
            return []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Parse the AST
            tree = ast.parse(content)

            # Extract code blocks
            code_blocks = self._extract_code_blocks(tree, file_path)

            # Index the blocks for future cross-file comparisons
            self._index_file_blocks(file_path, code_blocks)

            # Find duplicates within this file
            duplicates = self._find_similar_blocks(code_blocks)

            # Find cross-file duplicates
            cross_file_duplicates = self._find_cross_file_duplicates(
                file_path, code_blocks
            )

            # Combine all duplicates
            all_duplicates = {**duplicates, **cross_file_duplicates}

            # Convert to Duplication objects
            duplications: List[Duplication] = []
            for block_hash, locations in all_duplicates.items():
                if len(locations) > 1:  # Found duplicates
                    # Determine clone type based on similarity
                    clone_type = self._classify_clone_type(locations)
                    similarity = self._calculate_similarity(locations)

                    duplication = Duplication(
                        type=locations[0]["type"],
                        name=locations[0]["name"],
                        line=locations[0]["line"],
                        count=len(locations),
                        clone_type=clone_type,
                        similarity=similarity,
                        locations=[
                            {
                                "line": loc["line"],
                                "name": loc["name"],
                                "file": str(loc["file"]),
                            }
                            for loc in locations
                        ],
                    )
                    duplications.append(duplication)

            # Cache the results
            self._result_cache[cache_key] = (current_time, duplications)

            return duplications

        except Exception as e:
            print(f"Warning: Could not detect advanced duplicates for {file_path}: {e}")
            return []

    def _extract_code_blocks(
        self, tree: ast.AST, file_path: Path
    ) -> List[Dict[str, Any]]:
        """Extract code blocks from AST with normalization"""
        blocks = []

        # Walk the AST to find function and class definitions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Normalize the function AST
                normalized = self.normalizer.normalize_ast(node)

                # Extract function body as a block
                block_info = {
                    "type": "function",
                    "name": node.name,
                    "line": node.lineno,
                    "file": file_path,
                    "hash": normalized.structure_hash,
                    "normalized_ast": normalized,
                    "node": node,
                }
                blocks.append(block_info)
            elif isinstance(node, ast.ClassDef):
                # Normalize the class AST
                normalized = self.normalizer.normalize_ast(node)

                # Extract class body as a block
                block_info = {
                    "type": "class",
                    "name": node.name,
                    "line": node.lineno,
                    "file": file_path,
                    "hash": normalized.structure_hash,
                    "normalized_ast": normalized,
                    "node": node,
                }
                blocks.append(block_info)
            elif isinstance(node, (ast.For, ast.While, ast.If)):
                # Extract control structures as blocks
                normalized = self.normalizer.normalize_ast(node)

                block_info = {
                    "type": type(node).__name__.lower(),
                    "name": f"{type(node).__name__.lower()}_block",
                    "line": getattr(node, "lineno", 0),
                    "file": file_path,
                    "hash": normalized.structure_hash,
                    "normalized_ast": normalized,
                    "node": node,
                }
                blocks.append(block_info)

        return blocks

    def _find_similar_blocks(
        self, blocks: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Find similar code blocks using normalized ASTs"""
        duplicates: Dict[str, List[Dict[str, Any]]] = {}

        # Group blocks by hash (exact matches)
        for block in blocks:
            block_hash = block["hash"]
            if block_hash not in duplicates:
                duplicates[block_hash] = []
            duplicates[block_hash].append(block)

        # Filter to only include hashes with multiple occurrences
        duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}

        return duplicates

    def _index_file_blocks(self, file_path: Path, blocks: List[Dict[str, Any]]) -> None:
        """Index code blocks from a file for cross-file comparison"""
        self._file_cache[file_path] = blocks

        # Update file timestamp
        try:
            self._file_timestamps[file_path] = file_path.stat().st_mtime
        except OSError:
            self._file_timestamps[file_path] = time.time()

        # Remove old entries for this file from global index
        hashes_to_remove = []
        for block_hash, indexed_blocks in self._global_index.items():
            # Remove blocks from this file
            self._global_index[block_hash] = [
                block for block in indexed_blocks if block["file"] != file_path
            ]
            # If no blocks left for this hash, mark for removal
            if not self._global_index[block_hash]:
                hashes_to_remove.append(block_hash)

        # Remove empty hash entries
        for block_hash in hashes_to_remove:
            del self._global_index[block_hash]

        # Add new blocks to global index
        for block in blocks:
            block_hash = block["hash"]
            if block_hash not in self._global_index:
                self._global_index[block_hash] = []
            self._global_index[block_hash].append(block)

    def _cleanup_expired_cache(self) -> None:
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key
            for key, (cache_time, _) in self._result_cache.items()
            if current_time - cache_time >= self._cache_ttl
        ]

        for key in expired_keys:
            del self._result_cache[key]

    def _find_cross_file_duplicates(
        self, current_file: Path, blocks: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Find duplicates across different files"""
        duplicates: Dict[str, List[Dict[str, Any]]] = {}

        # Compare with blocks from other files
        for block_hash, indexed_blocks in self._global_index.items():
            # Find blocks with the same hash from different files
            cross_file_matches = [
                block for block in indexed_blocks if block["file"] != current_file
            ]

            # If we found matches in other files, check if any blocks in current file match
            if cross_file_matches:
                matching_current_blocks = [
                    block for block in blocks if block["hash"] == block_hash
                ]

                if matching_current_blocks:
                    # Combine all matching blocks
                    all_matching_blocks = matching_current_blocks + cross_file_matches
                    duplicates[block_hash] = all_matching_blocks

        return duplicates

    def _classify_clone_type(self, locations: List[Dict[str, Any]]) -> str:
        """Classify the type of clone based on similarity analysis"""
        if len(locations) > 1:
            # Check if all locations have identical structure hashes
            hashes = [loc.get("hash") for loc in locations]
            if len(set(hashes)) == 1:
                return "exact"  # Type-1 clone
            else:
                # Calculate average similarity
                avg_similarity = self._calculate_similarity(locations)
                if avg_similarity > 0.9:
                    return "renamed"  # Type-2 clone
                elif avg_similarity > 0.7:
                    return "modified"  # Type-3 clone
                else:
                    return "semantic"  # Type-4 clone

        return "exact"

    def _calculate_similarity(self, locations: List[Dict[str, Any]]) -> float:
        """Calculate similarity score between code blocks"""
        if len(locations) < 2:
            return 1.0

        # For now, we'll use a simplified approach
        # In a more advanced implementation, we would compare normalized ASTs
        # and calculate actual similarity scores

        # If all hashes are identical, similarity is 1.0
        hashes = [loc.get("hash") for loc in locations]
        if len(set(hashes)) == 1:
            return 1.0

        # For different hashes, return a lower similarity score
        # This is a placeholder - in a real implementation we would calculate actual similarity
        return 0.8


# Global instance for use in the scanner
advanced_duplicate_detector = AdvancedDuplicateDetector()
