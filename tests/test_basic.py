"""
Test file for Refactoroscope
"""

import tempfile
from pathlib import Path


def test_basic_functionality():
    """Test basic functionality of the Refactoroscope"""
    # Create a temporary directory with some test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create some test files
        (temp_path / "test.py").write_text(
            """
# This is a comment
def hello_world():
    print("Hello, World!")  # This is another comment
    
    if True:
        return "test"

class TestClass:
    def method(self):
        pass
"""
        )

        (temp_path / "test.js").write_text(
            """
// JavaScript comment
function hello() {
    console.log("Hello, World!");
    return true;
}
"""
        )

        # Create a .gitignore file
        (temp_path / ".gitignore").write_text(
            """
*.log
temp/
"""
        )

        # Try to import and use our modules
        try:
            from codeinsight.models.metrics import Language
            from codeinsight.scanner import Scanner

            # Test language detection
            scanner = Scanner()
            lang = scanner._detect_language(temp_path / "test.py")
            assert lang == Language.PYTHON, f"Expected PYTHON, got {lang}"

            lang = scanner._detect_language(temp_path / "test.js")
            assert lang == Language.JAVASCRIPT, f"Expected JAVASCRIPT, got {lang}"

            # Test line counting
            from codeinsight.analyzers.line_counter import LineCounter

            counter = LineCounter()
            loc, blank, comment = counter.count_lines(
                temp_path / "test.py", Language.PYTHON
            )

            # We should have some lines of code, blank lines, and comments
            assert loc > 0, f"Expected lines of code > 0, got {loc}"
            assert blank >= 0, f"Expected blank lines >= 0, got {blank}"
            assert comment > 0, f"Expected comment lines > 0, got {comment}"

            print("All basic tests passed!")

        except Exception as e:
            print(f"Test failed with error: {e}")
            raise


if __name__ == "__main__":
    test_basic_functionality()
