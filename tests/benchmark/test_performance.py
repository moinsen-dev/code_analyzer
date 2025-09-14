"""
Benchmark tests for Code Analyzer
"""

import pytest
from pathlib import Path
import time


def test_analysis_performance(benchmark):
    """Benchmark the analysis performance"""
    from codeinsight.scanner import Scanner

    # Create a scanner for the current directory
    scanner = Scanner()

    # Benchmark the analysis process
    def analyze_project():
        return scanner.analyze(Path(__file__).parent.parent)

    result = benchmark(analyze_project)

    # Should return results
    assert result is not None
    assert result.total_files > 0


def test_complexity_analysis_performance(benchmark):
    """Benchmark the complexity analysis performance"""
    from codeinsight.scanner import Scanner

    # Create a scanner with complexity analysis
    scanner = Scanner()

    # Benchmark the analysis process with complexity
    def analyze_project_with_complexity():
        return scanner.analyze(Path(__file__).parent.parent, include_complexity=True)

    result = benchmark(analyze_project_with_complexity)

    # Should return results
    assert result is not None
    assert result.total_files > 0
