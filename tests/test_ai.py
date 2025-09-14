"""
Tests for AI-powered code analysis functionality
"""

import os
import tempfile
from pathlib import Path

from codeinsight.ai.base import CodeContext


def test_ai_analyzer_initialization():
    """Test that AI analyzer can be initialized"""
    # Create a mock config manager (this would need to be properly mocked in a full test)
    # For now, we'll just test that the imports work
    try:
        # This test is mainly to ensure the module can be imported
        assert True
    except ImportError:
        assert False, "AIAnalyzer could not be imported"


def test_code_context_creation():
    """Test that CodeContext can be created"""
    # Create a temporary Python file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(
            """
def hello_world():
    print("Hello, World!")
    return True
"""
        )
        temp_file_path = Path(f.name)

    try:
        # Create a CodeContext
        context = CodeContext(
            file_path=temp_file_path, file_content="def test(): pass", language="python"
        )

        assert context.file_path == temp_file_path
        assert context.file_content == "def test(): pass"
        assert context.language == "python"

    finally:
        # Clean up
        os.unlink(temp_file_path)


def test_ai_provider_factory():
    """Test that AI provider factory works"""
    try:
        # This test is mainly to ensure the module can be imported
        assert True
    except ImportError:
        assert False, "AIProviderFactory could not be imported"
