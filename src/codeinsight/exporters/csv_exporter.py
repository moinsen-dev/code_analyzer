"""
CSV export functionality
"""

import csv
from pathlib import Path

from codeinsight.models.metrics import AnalysisReport


class CSVExporter:
    """Exports analysis reports to CSV format"""

    def export(self, report: AnalysisReport, output_path: Path) -> None:
        """
        Export report to CSV file

        Args:
            report: AnalysisReport to export
            output_path: Path to output file
        """
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(
                [
                    "File Path",
                    "Relative Path",
                    "Language",
                    "Lines of Code",
                    "Blank Lines",
                    "Comment Lines",
                    "Size (bytes)",
                    "Last Modified",
                    "Cyclomatic Complexity",
                    "Cognitive Complexity",
                    "Maintainability Index",
                    "Technical Debt Ratio",
                ]
            )

            # Write data rows
            for file_insight in report.top_files:
                file_metrics = file_insight.file_metrics
                complexity_metrics = file_insight.complexity_metrics

                row = [
                    str(file_metrics.path),
                    file_metrics.relative_path,
                    (
                        file_metrics.language.value
                        if hasattr(file_metrics.language, "value")
                        else str(file_metrics.language)
                    ),
                    file_metrics.lines_of_code,
                    file_metrics.blank_lines,
                    file_metrics.comment_lines,
                    file_metrics.size_bytes,
                    (
                        file_metrics.last_modified.isoformat()
                        if file_metrics.last_modified
                        else ""
                    ),
                ]

                # Add complexity metrics if available
                if complexity_metrics:
                    row.extend(
                        [
                            complexity_metrics.cyclomatic_complexity,
                            complexity_metrics.cognitive_complexity,
                            complexity_metrics.maintainability_index,
                            complexity_metrics.technical_debt_ratio,
                        ]
                    )
                else:
                    row.extend(["", "", "", ""])

                writer.writerow(row)
