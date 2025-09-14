"""
Test script to verify file filtering
"""

import tempfile
from pathlib import Path

from codeinsight.scanner import Scanner


def test_file_filtering():
    """Test file filtering functionality"""
    # Create a temporary directory with various file types
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create some test files
        (temp_path / "test.py").write_text(
            """
def hello():
    print("Hello, World!")
"""
        )

        (temp_path / "test.js").write_text(
            """
console.log("Hello, World!");
"""
        )

        # Create binary-like files that should be ignored
        (temp_path / "test.png").write_bytes(b"fake png content")
        (temp_path / "test.exe").write_bytes(b"fake executable")

        # Create large file that should be ignored
        large_file = temp_path / "large.txt"
        with open(large_file, "w") as f:
            f.write("x" * (Scanner.MAX_FILE_SIZE + 1000))  # Larger than max size

        # Create .git directory with files
        git_dir = temp_path / ".git"
        git_dir.mkdir()
        (git_dir / "test").write_text("git file content")

        # Create node_modules directory
        node_modules = temp_path / "node_modules"
        node_modules.mkdir()
        (node_modules / "test.js").write_text("node module content")

        # Test the scanner
        scanner = Scanner(temp_path)
        files = scanner._discover_files(temp_path)

        # Convert to relative paths for easier checking
        relative_files = [f.relative_to(temp_path) for f in files]
        file_names = [f.name for f in relative_files]

        print("Files that should be analyzed:")
        for f in relative_files:
            print(f"  {f}")

        # Verify that binary files are not included
        assert "test.png" not in file_names, "PNG files should be ignored"
        assert "test.exe" not in file_names, "EXE files should be ignored"
        assert "large.txt" not in file_names, "Large files should be ignored"

        # Verify that .git files are not included
        git_files = [f for f in relative_files if ".git" in str(f)]
        assert len(git_files) == 0, ".git files should be ignored"

        # Verify that node_modules files are not included
        node_files = [f for f in relative_files if "node_modules" in str(f)]
        assert len(node_files) == 0, "node_modules files should be ignored"

        # Verify that source files are included
        assert "test.py" in file_names, "Python files should be included"
        assert "test.js" in file_names, "JavaScript files should be included"

        print("File filtering test passed!")


if __name__ == "__main__":
    test_file_filtering()
