"""
Test script to simulate the original issue with .git files and images
"""

import tempfile
from pathlib import Path

from codeinsight.scanner import Scanner


def test_complex_filtering():
    """Test complex file filtering scenario"""
    # Create a temporary directory structure similar to the issue
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create source code files
        (temp_path / "main.dart").write_text(
            """
void main() {
  print('Hello, World!');
}
"""
        )

        (temp_path / "pubspec.yaml").write_text(
            """
name: test_app
description: A test application
"""
        )

        # Create .git directory with object files (like in the issue)
        git_dir = temp_path / ".git" / "objects" / "82"
        git_dir.mkdir(parents=True)
        (git_dir / "b6f9d9a33e198f5747104729e1fcef999772a5").write_bytes(b"x" * 10000)

        # Create image files (like in the issue)
        assets_dir = temp_path / "assets"
        assets_dir.mkdir()
        (assets_dir / "app_icon.png").write_bytes(b"x" * 50000)

        # Create large lock files
        (temp_path / "pubspec.lock").write_text(
            "\n".join([f"package{i}: 1.0.{i}" for i in range(1000)])
        )

        # Create node_modules with many files
        node_modules = temp_path / "node_modules"
        node_modules.mkdir()
        for i in range(50):
            (node_modules / f"module{i}.js").write_text(f"console.log('module {i}');")

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

        # Check that .git files are not in the results
        git_files = [
            f for f in report.top_files if ".git" in f.file_metrics.relative_path
        ]
        assert (
            len(git_files) == 0
        ), f"Found .git files in analysis: {[f.file_metrics.relative_path for f in git_files]}"

        # Check that image files are not in the results
        image_files = [
            f for f in report.top_files if ".png" in f.file_metrics.relative_path
        ]
        assert (
            len(image_files) == 0
        ), f"Found image files in analysis: {[f.file_metrics.relative_path for f in image_files]}"

        # Check that node_modules files are not in the results
        node_files = [
            f
            for f in report.top_files
            if "node_modules" in f.file_metrics.relative_path
        ]
        assert (
            len(node_files) == 0
        ), f"Found node_modules files in analysis: {[f.file_metrics.relative_path for f in node_files]}"

        # Check that source files are included
        source_files = [
            f
            for f in report.top_files
            if f.file_metrics.relative_path
            in ["main.dart", "pubspec.yaml", "pubspec.lock"]
        ]
        assert (
            len(source_files) >= 2
        ), f"Source files not properly included: {[f.file_metrics.relative_path for f in source_files]}"

        print("Complex filtering test passed!")
        print("Top files by line count:")
        for file_insight in report.top_files[:5]:
            print(
                f"  {file_insight.file_metrics.relative_path}: {file_insight.file_metrics.lines_of_code} lines"
            )


if __name__ == "__main__":
    test_complex_filtering()
