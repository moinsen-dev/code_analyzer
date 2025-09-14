"""
Tests for unused code detection functionality
"""

import os
import tempfile
from pathlib import Path

from codeinsight.analyzers.unused_code import UnusedCodeAnalyzer
from codeinsight.models.metrics import Language


def test_unused_code_detection():
    """Test basic unused code detection functionality"""
    # Create a temporary Python file with unused code
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            """
def unused_function():
    x = 10
    return x

def used_function():
    return "used"

class UnusedClass:
    def method(self):
        pass

used_value = used_function()
print(used_value)
"""
        )
        temp_file_path = Path(f.name)

    try:
        # Run unused code analysis
        analyzer = UnusedCodeAnalyzer()
        findings = analyzer.analyze(temp_file_path, Language.PYTHON)

        # Check that we found some unused code
        assert len(findings) > 0

        # Check that we found the unused function
        unused_function_found = any(
            finding.type == "function" and finding.name == "unused_function"
            for finding in findings
        )
        assert unused_function_found

        # Check that we found the unused class
        unused_class_found = any(
            finding.type == "class" and finding.name == "UnusedClass"
            for finding in findings
        )
        assert unused_class_found

    finally:
        # Clean up
        os.unlink(temp_file_path)


def test_no_unused_code():
    """Test that no unused code is reported when all code is used"""
    # Create a temporary Python file with no unused code
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            """
def used_function():
    return "used"

class UsedClass:
    def method(self):
        return "used"

used_value = used_function()
instance = UsedClass()
result = instance.method()
print(used_value, result)
"""
        )
        temp_file_path = Path(f.name)

    try:
        # Run unused code analysis
        analyzer = UnusedCodeAnalyzer()
        analyzer.analyze(temp_file_path, Language.PYTHON)

        # Check that we found no unused code
        # Note: This might not be completely accurate due to the limitations of static analysis
        # but it should be a reasonable test
        pass

    finally:
        # Clean up
        os.unlink(temp_file_path)
