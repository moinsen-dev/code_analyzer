"""
A third sample Python module for testing
"""

import math
from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class CodeMetrics:
    """Metrics for code analysis"""

    cyclomatic_complexity: float
    maintainability_index: float
    lines_of_code: int
    comment_ratio: float


class CodeAnalyzer:
    """Analyze code quality and complexity"""

    def __init__(self):
        self.metrics = []

    def analyze_code(self, code: str) -> CodeMetrics:
        """Analyze a piece of code and return metrics"""
        lines = code.splitlines()
        loc = len([line for line in lines if line.strip()])

        # Calculate comment ratio
        comments = len([line for line in lines if line.strip().startswith("#")])
        comment_ratio = comments / max(loc, 1)

        # Calculate cyclomatic complexity
        complexity = self._calculate_cyclomatic_complexity(code)

        # Estimate maintainability index
        maintainability = self._estimate_maintainability(code, loc, complexity)

        metrics = CodeMetrics(
            cyclomatic_complexity=complexity,
            maintainability_index=maintainability,
            lines_of_code=loc,
            comment_ratio=comment_ratio,
        )

        self.metrics.append(metrics)
        return metrics

    def _calculate_cyclomatic_complexity(self, code: str) -> float:
        """Calculate cyclomatic complexity of code"""
        # Count decision points
        decision_points = 0
        lines = code.splitlines()

        for line in lines:
            stripped = line.strip()
            if any(
                keyword in stripped
                for keyword in ["if ", "elif ", "for ", "while ", "except ", "case "]
            ):
                decision_points += 1
            elif " and " in stripped or " or " in stripped:
                decision_points += 1

        # Cyclomatic complexity = decision points + 1
        return decision_points + 1

    def _estimate_maintainability(
        self, code: str, loc: int, complexity: float
    ) -> float:
        """Estimate maintainability index"""
        # Simplified maintainability calculation
        # Based on lines of code and complexity
        if loc == 0:
            return 100.0

        # Maintainability index formula (simplified)
        mi = (
            171
            - 5.2 * math.log(max(1, complexity))
            - 0.23 * loc
            - 16.2 * math.log(max(1, 1))
        )
        return max(0, min(100, mi))

    def get_average_metrics(self) -> Optional[CodeMetrics]:
        """Get average metrics across all analyzed code"""
        if not self.metrics:
            return None

        total_cc = sum(m.cyclomatic_complexity for m in self.metrics)
        total_mi = sum(m.maintainability_index for m in self.metrics)
        total_loc = sum(m.lines_of_code for m in self.metrics)
        total_cr = sum(m.comment_ratio for m in self.metrics)

        count = len(self.metrics)

        return CodeMetrics(
            cyclomatic_complexity=total_cc / count,
            maintainability_index=total_mi / count,
            lines_of_code=int(total_loc / count),
            comment_ratio=total_cr / count,
        )


def process_multiple_files(file_paths: List[str]) -> Dict[str, CodeMetrics]:
    """Process multiple files and return metrics for each"""
    analyzer = CodeAnalyzer()
    results = {}

    for file_path in file_paths:
        try:
            with open(file_path, "r") as f:
                code = f.read()

            metrics = analyzer.analyze_code(code)
            results[file_path] = metrics

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            results[file_path] = None

    return results


def main():
    """Main function for demonstration"""
    files = ["module1.py", "module2.py"]
    results = process_multiple_files(files)

    for file_path, metrics in results.items():
        if metrics:
            print(f"File: {file_path}")
            print(f"  Cyclomatic Complexity: {metrics.cyclomatic_complexity}")
            print(f"  Maintainability Index: {metrics.maintainability_index:.2f}")
            print(f"  Lines of Code: {metrics.lines_of_code}")
            print(f"  Comment Ratio: {metrics.comment_ratio:.2f}")
        else:
            print(f"Failed to analyze {file_path}")


if __name__ == "__main__":
    main()
