"""
Another sample Python module for testing
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class FileAnalyzer:
    """Analyze files and extract metrics"""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.logger = logging.getLogger(__name__)

    def analyze_files(self, pattern: str = "*.py") -> Dict:
        """Analyze files matching the pattern"""
        results = {
            "total_files": 0,
            "total_lines": 0,
            "languages": {},
            "complexity": {},
        }

        # Find all matching files
        files = list(self.root_path.glob(f"**/{pattern}"))
        results["total_files"] = len(files)

        # Analyze each file
        for file_path in files:
            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()
                    results["total_lines"] += len(lines)

                    # Extract language info
                    extension = file_path.suffix
                    results["languages"][extension] = (
                        results["languages"].get(extension, 0) + 1
                    )

                    # Calculate complexity metrics
                    complexity = self._calculate_complexity(lines)
                    results["complexity"][str(file_path)] = complexity

            except Exception as e:
                self.logger.error(f"Error analyzing {file_path}: {e}")

        return results

    def _calculate_complexity(self, lines: List[str]) -> Dict:
        """Calculate complexity metrics for lines"""
        metrics = {
            "lines_of_code": 0,
            "comment_lines": 0,
            "blank_lines": 0,
            "functions": 0,
            "classes": 0,
            "conditionals": 0,
        }

        for line in lines:
            stripped = line.strip()
            if not stripped:
                metrics["blank_lines"] += 1
            elif stripped.startswith("#") or stripped.startswith("//"):
                metrics["comment_lines"] += 1
            else:
                metrics["lines_of_code"] += 1

                # Count functions and classes
                if stripped.startswith("def "):
                    metrics["functions"] += 1
                elif stripped.startswith("class "):
                    metrics["classes"] += 1

                # Count conditionals
                if "if " in stripped or "elif " in stripped or "else:" in stripped:
                    metrics["conditionals"] += 1
                elif "for " in stripped or "while " in stripped:
                    metrics["conditionals"] += 1

        return metrics


def generate_report(analyzer: FileAnalyzer, output_path: str = "report.json") -> bool:
    """Generate a JSON report from the analyzer"""
    try:
        results = analyzer.analyze_files()
        timestamp = datetime.now().isoformat()

        report = {"timestamp": timestamp, "results": results}

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        return True
    except Exception as e:
        logging.error(f"Error generating report: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = FileAnalyzer(".")
    success = generate_report(analyzer)
    if success:
        print("Report generated successfully")
    else:
        print("Failed to generate report")
