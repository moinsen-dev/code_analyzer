"""
Test script to verify configuration loading and usage
"""

import tempfile
from pathlib import Path

import yaml

from codeinsight.config.manager import ConfigManager
from codeinsight.scanner import Scanner


def test_configuration_loading():
    """Test that local .refactoroscope.yml is properly loaded and used"""
    # Create a temporary directory with a custom config
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a custom configuration file
        custom_config = {
            "version": 1.0,
            "languages": {
                "python": {"max_line_length": 100, "complexity_threshold": 15}
            },
            "analysis": {
                "ignore_patterns": ["*.custom.*", "custom_dir/"],
                "complexity": {"include_docstrings": True, "count_assertions": False},
                "thresholds": {
                    "file_too_long": 1000,
                    "function_too_complex": 30,
                    "class_too_large": 2000,
                },
            },
            "output": {
                "format": "terminal",
                "theme": "dark",
                "show_recommendations": False,
                "export_path": "./custom_reports",
            },
        }

        # Write the custom config
        config_path = temp_path / ".refactoroscope.yml"
        with open(config_path, "w") as f:
            yaml.dump(custom_config, f)

        # Create some test files
        (temp_path / "test.py").write_text(
            """
def hello():
    print("Hello, World!")
"""
        )

        # Create a file that should be ignored by our custom pattern
        (temp_path / "test.custom.py").write_text(
            """
def custom():
    print("This should be ignored")
"""
        )

        # Test the config manager
        config_manager = ConfigManager(temp_path)

        # Verify config is loaded correctly
        assert config_manager.config.version == 1.0
        assert config_manager.config.languages["python"].max_line_length == 100
        assert config_manager.config.languages["python"].complexity_threshold == 15
        assert "custom_dir/" in config_manager.config.analysis.ignore_patterns
        assert config_manager.config.output.theme == "dark"
        assert config_manager.config.output.show_recommendations is False

        # Test that the ignore patterns work
        assert config_manager.should_ignore_file(temp_path / "test.custom.py") is True

        # Test the scanner with the custom config
        scanner = Scanner(temp_path)
        report = scanner.analyze(temp_path)

        # Verify that the ignored file is not in the report
        ignored_files = [
            f
            for f in report.top_files
            if "test.custom.py" in f.file_metrics.relative_path
        ]
        assert (
            len(ignored_files) == 0
        ), "Custom ignored files should not appear in analysis"

        print("Configuration loading and usage test passed!")
        print(f"Loaded config version: {config_manager.config.version}")
        print(
            f"Python max line length: {config_manager.config.languages['python'].max_line_length}"
        )
        print(f"Output theme: {config_manager.config.output.theme}")
        print(f"Files analyzed: {report.total_files}")


if __name__ == "__main__":
    test_configuration_loading()
