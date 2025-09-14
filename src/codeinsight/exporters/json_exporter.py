"""
JSON export functionality
"""

from pathlib import Path

from codeinsight.models.metrics import AnalysisReport


class JSONExporter:
    """Exports analysis reports to JSON format"""

    def export(self, report: AnalysisReport, output_path: Path) -> None:
        """
        Export report to JSON file

        Args:
            report: AnalysisReport to export
            output_path: Path to output file
        """
        # Convert report to JSON and write to file
        with open(output_path, "w") as f:
            f.write(report.json())
