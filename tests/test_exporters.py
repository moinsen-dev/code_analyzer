"""
Test file for export functionality
"""

import tempfile
from datetime import datetime
from pathlib import Path

from codeinsight.exporters.csv_exporter import CSVExporter
from codeinsight.exporters.html_exporter import HTMLExporter
from codeinsight.exporters.json_exporter import JSONExporter
from codeinsight.models.metrics import (
    AnalysisReport,
    CodeInsights,
    ComplexityMetrics,
    FileMetrics,
    Language,
)


def test_exporters():
    """Test all export functionality"""
    # Create a sample report
    file_metrics = FileMetrics(
        path=Path("test.py"),
        relative_path="test.py",
        language=Language.PYTHON,
        lines_of_code=100,
        blank_lines=20,
        comment_lines=10,
        size_bytes=2048,
        last_modified=datetime.now(),
    )

    complexity_metrics = ComplexityMetrics(
        cyclomatic_complexity=5.5,
        cognitive_complexity=12.0,
        maintainability_index=75.5,
        technical_debt_ratio=5.0,
    )

    insights = CodeInsights(
        file_metrics=file_metrics, complexity_metrics=complexity_metrics
    )

    report = AnalysisReport(
        project_path=Path("."),
        timestamp=datetime.now(),
        total_files=1,
        total_lines=100,
        total_size=2048,
        language_distribution={Language.PYTHON: 1},
        top_files=[insights],
    )

    # Test with temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test JSON exporter
        json_exporter = JSONExporter()
        json_path = temp_path / "test.json"
        json_exporter.export(report, json_path)
        assert json_path.exists(), "JSON file should be created"
        assert json_path.stat().st_size > 0, "JSON file should not be empty"
        print("✓ JSON export test passed")

        # Test CSV exporter
        csv_exporter = CSVExporter()
        csv_path = temp_path / "test.csv"
        csv_exporter.export(report, csv_path)
        assert csv_path.exists(), "CSV file should be created"
        assert csv_path.stat().st_size > 0, "CSV file should not be empty"
        print("✓ CSV export test passed")

        # Test HTML exporter
        html_exporter = HTMLExporter()
        html_path = temp_path / "test.html"
        html_exporter.export(report, html_path)
        assert html_path.exists(), "HTML file should be created"
        assert html_path.stat().st_size > 0, "HTML file should not be empty"
        print("✓ HTML export test passed")

        print("All export tests passed!")


if __name__ == "__main__":
    test_exporters()
