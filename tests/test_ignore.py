"""
Test script to debug file ignoring
"""

from pathlib import Path

from codeinsight.config.manager import ConfigManager


def test_file_ignoring():
    """Test file ignoring functionality"""
    # Test with our sample project
    project_path = Path("examples/sample_project")
    config_manager = ConfigManager(project_path)

    print("Configuration loaded successfully!")
    print(f"Ignore patterns: {config_manager.config.analysis.ignore_patterns}")

    # List all files in the directory
    for file_path in project_path.iterdir():
        if file_path.is_file():
            should_ignore = config_manager.should_ignore_file(file_path)
            print(f"{file_path.name}: {'IGNORED' if should_ignore else 'INCLUDED'}")


if __name__ == "__main__":
    test_file_ignoring()
