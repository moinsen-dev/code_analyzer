"""
Benchmark tests for Code Insight Analyzer
"""
import pytest
from pathlib import Path
import time


def test_analysis_performance(benchmark):
    """Benchmark the analysis performance"""
    from codeinsight.scanner import CodeScanner
    
    # Create a scanner for the current directory
    scanner = CodeScanner()
    
    # Benchmark the scanning process
    def scan_project():
        return scanner.scan(Path(__file__).parent.parent)
    
    result = benchmark(scan_project)
    
    # Should return results
    assert result is not None
    assert len(result.files) > 0


def test_complexity_analysis_performance(benchmark):
    """Benchmark the complexity analysis performance"""
    from codeinsight.scanner import CodeScanner
    
    # Create a scanner with complexity analysis
    scanner = CodeScanner(include_complexity=True)
    
    # Benchmark the scanning process with complexity
    def scan_project_with_complexity():
        return scanner.scan(Path(__file__).parent.parent)
    
    result = benchmark(scan_project_with_complexity)
    
    # Should return results
    assert result is not None
    assert len(result.files) > 0