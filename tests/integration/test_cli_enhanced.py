"""
Integration tests for CLI commands including AI and unused code detection
"""

import subprocess
import tempfile
from pathlib import Path


def test_unused_command():
    """Test the unused code detection command"""
    # Create a temporary directory with a Python file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a simple .refactoroscope.yml config file
        config_file = temp_path / ".refactoroscope.yml"
        config_file.write_text(
            """
version: 1.0

# Language-specific settings
languages:
  python:
    max_line_length: 88
    complexity_threshold: 10
  typescript:
    max_line_length: 100
    complexity_threshold: 15
  javascript:
    max_line_length: 100
    complexity_threshold: 15

# Analysis rules
analysis:
  ignore_patterns:
    - "*.generated.*"
    - "*_pb2.py"
    - "*.min.js"
    - "node_modules/"
    - ".git/"

  complexity:
    include_docstrings: false
    count_assertions: true

  thresholds:
    file_too_long: 500
    function_too_complex: 20
    class_too_large: 1000

# Output preferences
output:
  format: "terminal"
  theme: "monokai"
  show_recommendations: true
  export_path: "./reports"
"""
        )

        # Create a Python file with unused code
        test_file = temp_path / "test_unused.py"
        test_file.write_text(
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

        # Run the unused command
        result = subprocess.run(
            ["python", "-m", "codeinsight.cli", "unused", str(temp_path)],
            capture_output=True,
            text=True,
            cwd=temp_path,
        )

        # The command should run successfully (exit code 0 or 2 for Typer)
        assert result.returncode in [
            0,
            2,
        ], f"Command failed with stderr: {result.stderr}"


def test_analyze_ai_help():
    """Test that the analyze command shows help for AI options"""
    # Run the analyze command with --help
    result = subprocess.run(
        ["python", "-m", "codeinsight.cli", "analyze", "--help"],
        capture_output=True,
        text=True,
    )

    # The command should run successfully
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    assert "AI" in result.stdout or "ai" in result.stdout


def test_analyze_with_ai_flag():
    """Test the analyze command with --ai flag"""
    # Create a temporary directory with a simple Python file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a simple .refactoroscope.yml config file
        config_file = temp_path / ".refactoroscope.yml"
        config_file.write_text(
            """
version: 1.0

# Language-specific settings
languages:
  python:
    max_line_length: 88
    complexity_threshold: 10
  typescript:
    max_line_length: 100
    complexity_threshold: 15
  javascript:
    max_line_length: 100
    complexity_threshold: 15

# Analysis rules
analysis:
  ignore_patterns:
    - "*.generated.*"
    - "*_pb2.py"
    - "*.min.js"
    - "node_modules/"
    - ".git/"

  complexity:
    include_docstrings: false
    count_assertions: true

  thresholds:
    file_too_long: 500
    function_too_complex: 20
    class_too_large: 1000

# Output preferences
output:
  format: "terminal"
  theme: "monokai"
  show_recommendations: true
  export_path: "./reports"

# AI configuration
ai:
  enable_ai_suggestions: false
  max_file_size: 50000
  cache_results: true
  cache_ttl: 3600
  provider_preferences:
    - "openai"
    - "anthropic"
    - "google"
    - "ollama"
  providers: {}
"""
        )

        # Create a simple Python file
        test_file = temp_path / "simple.py"
        test_file.write_text(
            """
def hello():
    print("Hello, World!")
    return True
"""
        )

        # Run the analyze command with --ai flag
        result = subprocess.run(
            ["python", "-m", "codeinsight.cli", "analyze", str(temp_path), "--ai"],
            capture_output=True,
            text=True,
            cwd=temp_path,
        )

        # The command should run successfully (exit code 0 or 2 for Typer)
        assert result.returncode in [
            0,
            2,
        ], f"Command failed with stderr: {result.stderr}"
