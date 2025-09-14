"""
Analysis report comparison functionality
"""

from typing import Any, Dict

from codeinsight.models.metrics import AnalysisReport


class ReportComparator:
    """Compares two analysis reports and generates insights"""

    def compare(
        self, report1: AnalysisReport, report2: AnalysisReport
    ) -> Dict[str, Any]:
        """
        Compare two analysis reports

        Args:
            report1: First analysis report
            report2: Second analysis report

        Returns:
            Dictionary with comparison results
        """
        comparison = {
            "summary": self._compare_summary(report1, report2),
            "files": self._compare_files(report1, report2),
            "languages": self._compare_languages(report1, report2),
            "complexity": self._compare_complexity(report1, report2),
        }

        return comparison

    def _compare_summary(
        self, report1: AnalysisReport, report2: AnalysisReport
    ) -> Dict[str, Any]:
        """Compare report summaries"""
        return {
            "total_files": {
                "report1": report1.total_files,
                "report2": report2.total_files,
                "difference": report2.total_files - report1.total_files,
                "percentage_change": self._calculate_percentage_change(
                    report1.total_files, report2.total_files
                ),
            },
            "total_lines": {
                "report1": report1.total_lines,
                "report2": report2.total_lines,
                "difference": report2.total_lines - report1.total_lines,
                "percentage_change": self._calculate_percentage_change(
                    report1.total_lines, report2.total_lines
                ),
            },
            "total_size": {
                "report1": report1.total_size,
                "report2": report2.total_size,
                "difference": report2.total_size - report1.total_size,
                "percentage_change": self._calculate_percentage_change(
                    report1.total_size, report2.total_size
                ),
            },
        }

    def _compare_files(
        self, report1: AnalysisReport, report2: AnalysisReport
    ) -> Dict[str, Any]:
        """Compare files between reports"""
        # Create dictionaries for easier lookup
        files1 = {f.file_metrics.relative_path: f for f in report1.top_files}
        files2 = {f.file_metrics.relative_path: f for f in report2.top_files}

        # Find new, removed, and changed files
        all_files = set(files1.keys()) | set(files2.keys())
        new_files = []
        removed_files = []
        changed_files = []

        for file_path in all_files:
            if file_path not in files1:
                new_files.append(
                    {
                        "path": file_path,
                        "lines": files2[file_path].file_metrics.lines_of_code,
                        "size": files2[file_path].file_metrics.size_bytes,
                    }
                )
            elif file_path not in files2:
                removed_files.append(
                    {
                        "path": file_path,
                        "lines": files1[file_path].file_metrics.lines_of_code,
                        "size": files1[file_path].file_metrics.size_bytes,
                    }
                )
            else:
                # File exists in both reports, check for changes
                file1 = files1[file_path]
                file2 = files2[file_path]

                lines_diff = (
                    file2.file_metrics.lines_of_code - file1.file_metrics.lines_of_code
                )
                size_diff = (
                    file2.file_metrics.size_bytes - file1.file_metrics.size_bytes
                )

                if lines_diff != 0 or size_diff != 0:
                    changed_files.append(
                        {
                            "path": file_path,
                            "lines_diff": lines_diff,
                            "size_diff": size_diff,
                            "lines1": file1.file_metrics.lines_of_code,
                            "lines2": file2.file_metrics.lines_of_code,
                            "size1": file1.file_metrics.size_bytes,
                            "size2": file2.file_metrics.size_bytes,
                        }
                    )

        return {
            "new_files": new_files,
            "removed_files": removed_files,
            "changed_files": changed_files,
        }

    def _compare_languages(
        self, report1: AnalysisReport, report2: AnalysisReport
    ) -> Dict[str, Any]:
        """Compare language distributions"""
        all_languages = set(report1.language_distribution.keys()) | set(
            report2.language_distribution.keys()
        )

        language_changes = {}
        for lang in all_languages:
            count1 = report1.language_distribution.get(lang, 0)
            count2 = report2.language_distribution.get(lang, 0)

            language_changes[lang.value] = {
                "report1": count1,
                "report2": count2,
                "difference": count2 - count1,
                "percentage_change": self._calculate_percentage_change(count1, count2),
            }

        return language_changes

    def _compare_complexity(
        self, report1: AnalysisReport, report2: AnalysisReport
    ) -> Dict[str, Any]:
        """Compare complexity metrics"""
        # Get files with complexity metrics from both reports
        complexity_files1 = {
            f.file_metrics.relative_path: f.complexity_metrics
            for f in report1.top_files
            if f.complexity_metrics
        }
        complexity_files2 = {
            f.file_metrics.relative_path: f.complexity_metrics
            for f in report2.top_files
            if f.complexity_metrics
        }

        # Find common files with complexity metrics
        common_files = set(complexity_files1.keys()) & set(complexity_files2.keys())

        complexity_changes = {}
        for file_path in common_files:
            comp1 = complexity_files1[file_path]
            comp2 = complexity_files2[file_path]

            complexity_changes[file_path] = {
                "cyclomatic": {
                    "report1": comp1.cyclomatic_complexity,
                    "report2": comp2.cyclomatic_complexity,
                    "difference": comp2.cyclomatic_complexity
                    - comp1.cyclomatic_complexity,
                },
                "maintainability": {
                    "report1": comp1.maintainability_index,
                    "report2": comp2.maintainability_index,
                    "difference": comp2.maintainability_index
                    - comp1.maintainability_index,
                },
            }

        return {
            "files_with_changes": complexity_changes,
            "total_files_with_complexity_report1": len(complexity_files1),
            "total_files_with_complexity_report2": len(complexity_files2),
        }

    def _calculate_percentage_change(self, old_value: float, new_value: float) -> float:
        """Calculate percentage change between two values"""
        if old_value == 0:
            return 100.0 if new_value > 0 else 0.0
        return ((new_value - old_value) / old_value) * 100
