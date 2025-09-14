"""
GitIgnore parsing and matching utilities
"""

from pathlib import Path
from typing import Dict, Optional

try:
    import pathspec

    PATHSPEC_AVAILABLE = True
except ImportError:
    PATHSPEC_AVAILABLE = False


class GitIgnoreMatcher:
    """Matches files and directories against .gitignore patterns"""

    def __init__(self) -> None:
        self.specs: Dict[Path, pathspec.GitIgnoreSpec] = (
            {}
        )  # directory -> pathspec.GitIgnoreSpec
        self.root_path: Optional[Path] = None

    def update_for_directory(self, directory: Path) -> None:
        """
        Load .gitignore patterns for a directory and its parents

        Args:
            directory: Directory to load .gitignore for
        """
        if not PATHSPEC_AVAILABLE:
            return

        # Store root path
        if self.root_path is None:
            self.root_path = directory

        # Collect all .gitignore files from directory up to root
        gitignore_paths = []
        current = directory.resolve()

        while current >= self.root_path.resolve():
            gitignore_path = current / ".gitignore"
            if gitignore_path.exists():
                gitignore_paths.append(gitignore_path)

            if current == current.parent:  # Reached filesystem root
                break
            current = current.parent

        # Combine all patterns
        patterns = []
        for gitignore_path in reversed(gitignore_paths):  # Parent first
            try:
                with open(gitignore_path, "r") as f:
                    patterns.extend(f.read().splitlines())
            except Exception:
                pass  # Skip unreadable files - acceptable fallback

        # Create spec if we have patterns
        if patterns:
            self.specs[directory] = pathspec.GitIgnoreSpec.from_lines(patterns)
        elif directory in self.specs:
            del self.specs[directory]

    def matches_file(self, file_path: Path) -> bool:
        """
        Check if a file matches any .gitignore pattern

        Args:
            file_path: Path to file to check

        Returns:
            True if file should be ignored
        """
        if not PATHSPEC_AVAILABLE:
            return False

        # Check each spec
        for directory, spec in self.specs.items():
            try:
                # Get path relative to the directory with the .gitignore
                relative_path = file_path.relative_to(directory)
                if spec.match_file(str(relative_path)):
                    return True
            except ValueError:
                # file_path is not relative to directory, skip
                continue

        return False

    def matches_directory(self, dir_path: Path) -> bool:
        """
        Check if a directory matches any .gitignore pattern

        Args:
            dir_path: Path to directory to check

        Returns:
            True if directory should be ignored
        """
        if not PATHSPEC_AVAILABLE:
            return False

        # Check each spec
        for directory, spec in self.specs.items():
            try:
                # Get path relative to the directory with the .gitignore
                relative_path = dir_path.relative_to(directory)
                # Check if the directory itself is ignored
                if spec.match_file(str(relative_path) + "/"):
                    return True
                # Check if everything in the directory is ignored
                if spec.match_file(str(relative_path) + "/**"):
                    return True
            except ValueError:
                # dir_path is not relative to directory, skip
                continue

        return False
