"""
Test script to verify filtering of *lock.yaml files
"""

import tempfile
from pathlib import Path

from codeinsight.scanner import Scanner


def test_lock_yaml_filtering():
    """Test filtering of *lock.yaml files"""
    # Create a temporary directory with lock.yaml files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create actual source files that should be analyzed
        (temp_path / "main.py").write_text(
            """
def main():
    print('Hello, World!')

if __name__ == "__main__":
    main()
"""
        )

        # Create lock.yaml files that should be ignored
        (temp_path / "dependencies-lock.yaml").write_text(
            """
# Generated dependencies lock file
packages:
  - name: requests
    version: "2.31.0"
  - name: numpy
    version: "1.24.3"
"""
        )

        (temp_path / "environment-lock.yaml").write_text(
            """
# Generated environment lock file
name: test-env
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pip
"""
        )

        # Create regular YAML files that should be analyzed
        (temp_path / "config.yaml").write_text(
            """
# Configuration file
server:
  host: localhost
  port: 8080
database:
  url: postgresql://localhost:5432/test
"""
        )

        (temp_path / "docker-compose.yaml").write_text(
            """
# Docker compose file
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8080:8080"
"""
        )

        print(f"Created test directory with {len(list(temp_path.rglob('*')))} files")

        # Test the scanner
        scanner = Scanner(temp_path)
        report = scanner.analyze(temp_path)

        print(f"Analysis found {report.total_files} files")
        print(f"Total lines of code: {report.total_lines}")
        print(f"Total size: {report.total_size:,} bytes")
        print(
            "Languages:",
            {lang.value: count for lang, count in report.language_distribution.items()},
        )

        # Check that lock.yaml files are not in the results
        lock_yaml_files = [
            f for f in report.top_files if "lock.yaml" in f.file_metrics.relative_path
        ]
        assert (
            len(lock_yaml_files) == 0
        ), f"Found lock.yaml files in analysis: {[f.file_metrics.relative_path for f in lock_yaml_files]}"

        # Check that regular YAML files are still included
        yaml_files = [
            f
            for f in report.top_files
            if f.file_metrics.relative_path.endswith((".yaml", ".yml"))
            and "lock.yaml" not in f.file_metrics.relative_path
        ]
        assert (
            len(yaml_files) >= 2
        ), f"Regular YAML files not properly included: {[f.file_metrics.relative_path for f in yaml_files]}"

        # Check that source files are included
        source_files = [
            f for f in report.top_files if f.file_metrics.relative_path == "main.py"
        ]
        assert (
            len(source_files) >= 1
        ), f"Source files not properly included: {[f.file_metrics.relative_path for f in source_files]}"

        print("Lock.yaml file filtering test passed!")
        print("Files that were analyzed:")
        for file_insight in report.top_files:
            print(
                f"  {file_insight.file_metrics.relative_path}: {file_insight.file_metrics.lines_of_code} lines"
            )


if __name__ == "__main__":
    test_lock_yaml_filtering()
