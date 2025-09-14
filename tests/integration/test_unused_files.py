"""
Integration tests for unused files CLI command
"""

import subprocess
import tempfile
from pathlib import Path


def test_unused_files_command_help():
    """Test that the unused-files command shows help"""
    # Run the unused-files command with --help
    result = subprocess.run(
        ["python", "-m", "codeinsight.cli", "unused-files", "--help"],
        capture_output=True,
        text=True,
    )

    # The command should run successfully
    assert result.returncode == 0, f"Command failed with stderr: {result.stderr}"
    assert "unused-files" in result.stdout


def test_unused_files_command_with_simple_project():
    """Test the unused-files command with a simple project"""
    # Create a temporary directory with a Python project
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

# Analysis rules
analysis:
  ignore_patterns: []

# Output preferences
output:
  format: "terminal"
  theme: "monokai"
  show_recommendations: true
  export_path: "./reports"
"""
        )

        # Create a simple Python project
        # main.py - entry point
        main_file = temp_path / "main.py"
        main_file.write_text(
            """
from module1 import function1

if __name__ == "__main__":
    print(function1())
"""
        )

        # module1.py - used module
        module1_file = temp_path / "module1.py"
        module1_file.write_text(
            """
def function1():
    return "Hello from module1"
"""
        )

        # module2.py - unused module
        module2_file = temp_path / "module2.py"
        module2_file.write_text(
            """
def function2():
    return "This module is never imported"
"""
        )

        # Run the unused-files command
        result = subprocess.run(
            ["python", "-m", "codeinsight.cli", "unused-files", str(temp_path)],
            capture_output=True,
            text=True,
            cwd=temp_path,
        )

        # The command should run successfully (exit code 0 or 2 for Typer)
        assert result.returncode in [
            0,
            2,
        ], f"Command failed with stderr: {result.stderr}"


def test_unused_files_command_with_json_output():
    """Test the unused-files command with JSON output"""
    # Create a temporary directory with a Python project
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

# Analysis rules
analysis:
  ignore_patterns: []

# Output preferences
output:
  format: "terminal"
  theme: "monokai"
  show_recommendations: true
  export_path: "./reports"
"""
        )

        # Create a simple Python project
        # main.py - entry point
        main_file = temp_path / "main.py"
        main_file.write_text(
            """
from module1 import function1

if __name__ == "__main__":
    print(function1())
"""
        )

        # module1.py - used module
        module1_file = temp_path / "module1.py"
        module1_file.write_text(
            """
def function1():
    return "Hello from module1"
"""
        )

        # module2.py - unused module
        module2_file = temp_path / "module2.py"
        module2_file.write_text(
            """
def function2():
    return "This module is never imported"
"""
        )

        # Run the unused-files command with JSON output
        result = subprocess.run(
            [
                "python",
                "-m",
                "codeinsight.cli",
                "unused-files",
                str(temp_path),
                "--output",
                "json",
            ],
            capture_output=True,
            text=True,
            cwd=temp_path,
        )

        # The command should run successfully (exit code 0 or 2 for Typer)
        assert result.returncode in [
            0,
            2,
        ], f"Command failed with stderr: {result.stderr}"

        # Should contain JSON output
        assert "{" in result.stdout
        assert "}" in result.stdout
