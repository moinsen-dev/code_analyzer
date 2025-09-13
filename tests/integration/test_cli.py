"""
Integration tests for Code Insight Analyzer
"""
import subprocess
import sys
from pathlib import Path


def test_cli_integration():
    """Test that the CLI can be invoked and runs successfully"""
    # Run a basic analysis on the examples directory
    result = subprocess.run(
        ["code_analyzer", "analyze", "."]
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    
    # Should exit successfully (0) or with analysis results (2)
    # Exit code 2 is used for successful analysis with findings
    assert result.returncode in [0, 2], f"Command failed with stderr: {result.stderr}"
    
    # Should produce some output
    assert len(result.stdout) > 0
    
    # Should not have any critical errors
    assert "error" not in result.stderr.lower() or "no error" in result.stderr.lower()


def test_cli_complexity_integration():
    """Test that the CLI can run complexity analysis"""
    # Run analysis with complexity on the examples directory
    result = subprocess.run(
        ["code_analyzer", "analyze", ".", "--complexity"]
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )
    
    # Should exit successfully (0) or with analysis results (2)
    # Exit code 2 is used for successful analysis with findings
    assert result.returncode in [0, 2], f"Command failed with stderr: {result.stderr}"
    
    # Should produce output
    assert len(result.stdout) > 0