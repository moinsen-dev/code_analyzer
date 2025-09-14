"""
Test script for configuration manager
"""

from pathlib import Path

from codeinsight.config.manager import ConfigManager


def test_config():
    """Test the configuration manager"""
    # Test with our sample project
    project_path = Path("examples/sample_project")
    config_manager = ConfigManager(project_path)

    print("Configuration loaded successfully!")
    print(f"Version: {config_manager.config.version}")
    print(f"Languages: {list(config_manager.config.languages.keys())}")
    print(f"Ignore patterns: {config_manager.config.analysis.ignore_patterns}")

    # Test if a file should be ignored
    test_file = project_path / "test.generated.js"
    should_ignore = config_manager.should_ignore_file(test_file)
    print(f"Should ignore {test_file.name}: {should_ignore}")

    # Test with a normal file
    normal_file = project_path / "calculator.py"
    should_ignore_normal = config_manager.should_ignore_file(normal_file)
    print(f"Should ignore {normal_file.name}: {should_ignore_normal}")


if __name__ == "__main__":
    test_config()
