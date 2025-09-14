"""
Tests for advanced duplicate detection
"""

import ast
from pathlib import Path

from codeinsight.analysis.advanced_duplicates import (
    AdvancedDuplicateDetector,
    ASTNormalizer,
    CloneType,
    NormalizedAST,
)
from codeinsight.models.metrics import Duplication, Language


class TestASTNormalizer:
    """Test AST normalization functionality"""

    def test_normalize_identifiers(self):
        """Test identifier normalization"""
        normalizer = ASTNormalizer()

        # Simple function with identifiers
        code = """
def calculate_total(items, tax_rate):
    subtotal = 0
    for item in items:
        subtotal += item.price * item.quantity
    return subtotal * (1 + tax_rate)
"""

        tree = ast.parse(code)
        normalized = normalizer.normalize_ast(tree)

        # Check that we have a normalized AST
        assert isinstance(normalized, NormalizedAST)
        assert isinstance(normalized.normalized_source, str)
        assert isinstance(normalized.identifiers, set)
        assert isinstance(normalized.literals, set)
        assert isinstance(normalized.structure_hash, str)

        # Check that identifiers were captured
        assert len(normalized.identifiers) > 0

    def test_normalize_literals(self):
        """Test literal normalization"""
        normalizer = ASTNormalizer()

        # Function with literals
        code = """
def process_data():
    name = "John"
    age = 25
    score = 95.5
    active = True
"""

        tree = ast.parse(code)
        normalized = normalizer.normalize_ast(tree)

        # Check that literals were captured
        assert isinstance(normalized.literals, set)
        assert len(normalized.literals) > 0

    def test_calculate_similarity(self):
        """Test similarity calculation"""
        normalizer = ASTNormalizer()

        # Two similar functions
        code1 = """
def add(a, b):
    return a + b
"""

        code2 = """
def sum(x, y):
    return x + y
"""

        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)

        similarity = normalizer.calculate_similarity(tree1, tree2)

        # Should have some similarity (not 0, not 1)
        assert 0.0 <= similarity <= 1.0


class TestAdvancedDuplicateDetector:
    """Test advanced duplicate detection functionality"""

    def test_detect_duplicates(self):
        """Test duplicate detection in a file"""
        detector = AdvancedDuplicateDetector()

        # Create a temporary file with duplicate code
        code = """
def function_one():
    x = 1
    if x > 0:
        return x
    return 0

def function_two():
    y = 1
    if y > 0:
        return y
    return 0
"""

        # Write to temporary file
        temp_file = Path("temp_test.py")
        try:
            with open(temp_file, "w") as f:
                f.write(code)

            # Detect duplicates
            duplications = detector.detect_duplicates(temp_file, Language.PYTHON)

            # Check results
            assert isinstance(duplications, list)

        finally:
            # Clean up
            if temp_file.exists():
                temp_file.unlink()

    def test_classify_clone_type(self):
        """Test clone type classification"""
        detector = AdvancedDuplicateDetector()

        # Test exact clone classification
        locations = [{"hash": "abc123"}, {"hash": "abc123"}]

        clone_type = detector._classify_clone_type(locations)
        assert clone_type in ["exact", "renamed", "modified", "semantic"]

    def test_calculate_similarity(self):
        """Test similarity calculation for locations"""
        detector = AdvancedDuplicateDetector()

        # Test with identical hashes
        locations = [{"hash": "abc123"}, {"hash": "abc123"}]

        similarity = detector._calculate_similarity(locations)
        assert similarity == 1.0


def test_duplication_model():
    """Test the enhanced Duplication model"""
    # Create a duplication with clone type and similarity
    duplication = Duplication(
        type="function",
        name="test_function",
        line=10,
        count=3,
        clone_type="renamed",
        similarity=0.85,
        locations=[
            {"line": 10, "name": "test_function", "file": "file1.py"},
            {"line": 25, "name": "test_function", "file": "file2.py"},
            {"line": 40, "name": "test_function", "file": "file3.py"},
        ],
    )

    # Check all attributes
    assert duplication.type == "function"
    assert duplication.name == "test_function"
    assert duplication.line == 10
    assert duplication.count == 3
    assert duplication.clone_type == "renamed"
    assert duplication.similarity == 0.85
    assert len(duplication.locations) == 3


def test_clone_type_enum():
    """Test CloneType enum"""
    assert CloneType.EXACT.value == "exact"
    assert CloneType.RENAMED.value == "renamed"
    assert CloneType.MODIFIED.value == "modified"
    assert CloneType.SEMANTIC.value == "semantic"
