"""
Tests for unused file detection functionality
"""

import tempfile
from pathlib import Path

from codeinsight.analyzers.unused_files import (
    FileDependencyGraphBuilder,
    UnusedFileAnalyzer,
)
from codeinsight.config.manager import ConfigManager


def test_unused_file_analyzer_initialization():
    """Test that UnusedFileAnalyzer can be initialized"""
    analyzer = UnusedFileAnalyzer()
    assert analyzer is not None


def test_file_dependency_graph_builder_initialization():
    """Test that FileDependencyGraphBuilder can be initialized"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_manager = ConfigManager(temp_path)

        builder = FileDependencyGraphBuilder(temp_path, config_manager)
        assert builder is not None


def test_unused_file_detection_with_simple_project():
    """Test unused file detection with a simple project structure"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a simple Python project
        # main.py - entry point
        main_file = temp_path / "main.py"
        main_file.write_text(
            """
from module1 import function1

if __name__ == "__main__":
    print(function1())
"""
        )

        # module1.py - used module
        module1_file = temp_path / "module1.py"
        module1_file.write_text(
            """
def function1():
    return "Hello from module1"

def unused_function():
    return "This function is never used"
"""
        )

        # module2.py - unused module
        module2_file = temp_path / "module2.py"
        module2_file.write_text(
            """
def function2():
    return "This module is never imported"
"""
        )

        # Create config manager
        config_manager = ConfigManager(temp_path)

        # Run unused file analysis
        analyzer = UnusedFileAnalyzer()
        findings = analyzer.analyze(temp_path, config_manager)

        # Print findings for debugging
        print(f"Findings: {findings}")
        for finding in findings:
            print(
                f"  Path: {finding.path}, Confidence: {finding.confidence}, Reason: {finding.reason}"
            )

        # Check that module2.py is identified as unused (it should have high confidence)
        module2_findings = [f for f in findings if "module2.py" in str(f.path)]
        assert len(module2_findings) >= 1, "module2.py should be detected as unused"

        # Check that main.py and module1.py are not flagged as unused (or have low confidence)
        main_findings = [
            f for f in findings if "main.py" in str(f.path) and f.confidence > 0.7
        ]
        module1_findings = [
            f for f in findings if "module1.py" in str(f.path) and f.confidence > 0.7
        ]
        assert (
            len(main_findings) == 0
        ), "main.py should not be detected as unused with high confidence"
        assert (
            len(module1_findings) == 0
        ), "module1.py should not be detected as unused with high confidence"


def test_unused_file_detection_with_truly_unused_file():
    """Test unused file detection with a truly unused file"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a Python project with a truly unused file
        # main.py - entry point with no imports
        main_file = temp_path / "main.py"
        main_file.write_text(
            """
def main():
    print("Hello World")
    
if __name__ == "__main__":
    main()
"""
        )

        # unused_module.py - completely unused module
        unused_module_file = temp_path / "unused_module.py"
        unused_module_file.write_text(
            """
def unused_function():
    return "This module is never imported or referenced"
"""
        )

        # another_unused.py - another completely unused module
        another_unused_file = temp_path / "another_unused.py"
        another_unused_file.write_text(
            """
def another_unused_function():
    return "This module is also never imported or referenced"
"""
        )

        # Create config manager
        config_manager = ConfigManager(temp_path)

        # Run unused file analysis
        analyzer = UnusedFileAnalyzer()
        findings = analyzer.analyze(temp_path, config_manager)

        # Print findings for debugging
        print(f"Findings: {findings}")
        for finding in findings:
            print(
                f"  Path: {finding.path}, Confidence: {finding.confidence}, Reason: {finding.reason}"
            )

        # Check that we found unused files with high confidence
        high_confidence_findings = [f for f in findings if f.confidence >= 0.7]
        assert (
            len(high_confidence_findings) >= 1
        ), "Should detect at least one unused file with high confidence"

        # Check that unused_module.py is identified as unused
        unused_module_findings = [
            f for f in findings if "unused_module.py" in str(f.path)
        ]
        assert (
            len(unused_module_findings) >= 1
        ), "unused_module.py should be detected as unused"


def test_unused_file_detection_with_entry_point():
    """Test unused file detection with explicit entry point"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a Python project with an entry point
        # app.py - entry point
        app_file = temp_path / "app.py"
        app_file.write_text(
            """
from utils import helper

def main():
    print(helper())
    
if __name__ == "__main__":
    main()
"""
        )

        # utils.py - used module
        utils_file = temp_path / "utils.py"
        utils_file.write_text(
            """
def helper():
    return "Helper function"
"""
        )

        # unused_module.py - unused module
        unused_module_file = temp_path / "unused_module.py"
        unused_module_file.write_text(
            """
def unused_function():
    return "This module is never imported"
"""
        )

        # Create config manager
        config_manager = ConfigManager(temp_path)

        # Run unused file analysis
        analyzer = UnusedFileAnalyzer()
        findings = analyzer.analyze(temp_path, config_manager)

        # Print findings for debugging
        print(f"Findings: {findings}")
        for finding in findings:
            print(
                f"  Path: {finding.path}, Confidence: {finding.confidence}, Reason: {finding.reason}"
            )

        # Check that unused_module.py is identified as unused (it should have high confidence)
        unused_module_findings = [
            f for f in findings if "unused_module.py" in str(f.path)
        ]
        assert (
            len(unused_module_findings) >= 1
        ), "unused_module.py should be detected as unused"

        # Check that app.py and utils.py are not flagged as unused (or have low confidence)
        app_findings = [
            f for f in findings if "app.py" in str(f.path) and f.confidence > 0.7
        ]
        utils_findings = [
            f for f in findings if "utils.py" in str(f.path) and f.confidence > 0.7
        ]
        assert (
            len(app_findings) == 0
        ), "app.py should not be detected as unused with high confidence"
        assert (
            len(utils_findings) == 0
        ), "utils.py should not be detected as unused with high confidence"
