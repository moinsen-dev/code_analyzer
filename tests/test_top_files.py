"""
Test script to verify the --top-files option
"""

from typer.testing import CliRunner

from codeinsight.cli import app


def test_top_files_option():
    """Test the --top-files option"""
    runner = CliRunner()

    # Test with a small project
    result = runner.invoke(
        app, ["analyze", "examples/sample_project", "--top-files", "3"]
    )
    assert result.exit_code == 0
    assert "Top Files by Line Count (Top 3)" in result.stdout
    assert "smelly.py" in result.stdout
    assert "calculator.py" in result.stdout
    # README.md is the 6th file, so it won't be shown with --top-files 3

    # Test default behavior (should show Top 20)
    result = runner.invoke(app, ["analyze", "examples/sample_project"])
    assert result.exit_code == 0
    assert "Top Files by Line Count (Top 20)" in result.stdout

    # Test with a larger number
    result = runner.invoke(
        app, ["analyze", "examples/sample_project", "--top-files", "100"]
    )
    assert result.exit_code == 0
    assert "Top Files by Line Count (Top 100)" in result.stdout

    print("Top files option test passed!")


if __name__ == "__main__":
    test_top_files_option()
