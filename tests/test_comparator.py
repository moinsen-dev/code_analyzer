"""
Test script for report comparator
"""

from datetime import datetime
from pathlib import Path

from codeinsight.analysis.comparator import ReportComparator
from codeinsight.models.metrics import AnalysisReport, Language


def test_comparator():
    """Test the report comparator functionality"""
    # Create mock report data
    report1 = AnalysisReport(
        project_path=Path("."),
        timestamp=datetime.now(),
        total_files=10,
        total_lines=1000,
        total_size=50000,
        language_distribution={Language.PYTHON: 10},
        top_files=[],
        recommendations=[],
    )

    report2 = AnalysisReport(
        project_path=Path("."),
        timestamp=datetime.now(),
        total_files=12,  # Increased from 10
        total_lines=1200,  # Increased from 1000
        total_size=55000,  # Increased from 50000
        language_distribution={Language.PYTHON: 12},
        top_files=[],
        recommendations=[],
    )

    # Compare the reports
    comparator = ReportComparator()
    comparison = comparator.compare(report1, report2)

    # Verify the comparison results
    assert comparison is not None
    assert comparison["summary"]["total_files"]["difference"] == 2
    assert comparison["summary"]["total_lines"]["difference"] == 200
    assert comparison["summary"]["total_size"]["difference"] == 5000


def test_comparator_with_file_changes():
    """Test the report comparator with file changes"""

    # Create reports with file data
    report1 = AnalysisReport(
        project_path=Path("."),
        timestamp=datetime.now(),
        total_files=1,
        total_lines=100,
        total_size=2000,
        language_distribution={Language.PYTHON: 1},
        top_files=[],
        recommendations=[],
    )

    report2 = AnalysisReport(
        project_path=Path("."),
        timestamp=datetime.now(),
        total_files=1,
        total_lines=150,
        total_size=2500,
        language_distribution={Language.PYTHON: 1},
        top_files=[],
        recommendations=[],
    )

    # Compare the reports
    comparator = ReportComparator()
    comparison = comparator.compare(report1, report2)

    # Verify the comparison results
    assert comparison is not None
    assert comparison["summary"]["total_lines"]["difference"] == 50
    assert comparison["summary"]["total_size"]["difference"] == 500
