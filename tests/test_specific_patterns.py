"""
Test script to verify filtering of specific file patterns
"""

import tempfile
from pathlib import Path

from codeinsight.scanner import Scanner


def test_specific_file_pattern_filtering():
    """Test filtering of specific file patterns like *-lock.json and *.freezed.dart"""
    # Create a temporary directory with the specific file patterns mentioned
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create actual source files that should be analyzed
        (temp_path / "main.dart").write_text(
            """
void main() {
  print('Hello, World!');
}
"""
        )

        (temp_path / "user.dart").write_text(
            """
class User {
  String name;
  int age;
  
  User(this.name, this.age);
}
"""
        )

        # Create specific generated files that should be ignored
        (temp_path / "user.freezed.dart").write_text(
            """
// GENERATED CODE - DO NOT MODIFY BY HAND
// This is a generated freezed file
class _$User {
  // Lots of generated code...
}
"""
        )

        # Create specific lock files that should be ignored
        (temp_path / "flutter-lock.json").write_text(
            """
{
  "packages": {
    "flutter": {
      "version": "3.10.0"
    }
  }
}
"""
        )

        (temp_path / "dependencies-lock.json").write_text(
            """
{
  "packages": {
    "http": {
      "version": "0.14.0"
    }
  }
}
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

        # Check that specific generated files are not in the results
        freezed_files = [
            f
            for f in report.top_files
            if ".freezed.dart" in f.file_metrics.relative_path
        ]
        assert (
            len(freezed_files) == 0
        ), f"Found freezed files in analysis: {[f.file_metrics.relative_path for f in freezed_files]}"

        # Check that specific lock files are not in the results
        lock_files = [
            f for f in report.top_files if "-lock.json" in f.file_metrics.relative_path
        ]
        assert (
            len(lock_files) == 0
        ), f"Found lock files in analysis: {[f.file_metrics.relative_path for f in lock_files]}"

        # Check that source files are included
        source_files = [
            f
            for f in report.top_files
            if f.file_metrics.relative_path in ["main.dart", "user.dart"]
        ]
        assert (
            len(source_files) >= 1
        ), f"Source files not properly included: {[f.file_metrics.relative_path for f in source_files]}"

        print("Specific file pattern filtering test passed!")
        print("Files that were analyzed:")
        for file_insight in report.top_files:
            print(
                f"  {file_insight.file_metrics.relative_path}: {file_insight.file_metrics.lines_of_code} lines"
            )


if __name__ == "__main__":
    test_specific_file_pattern_filtering()
