"""
Tech Stack Detector for Refactoroscope
Detects technology stacks in project folders
"""

from pathlib import Path
from typing import Dict, List


class TechStackDetector:
    """Detects technology stacks in project folders"""

    def __init__(self) -> None:
        # Define tech stack indicators
        self.indicators = {
            "python": {
                "files": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
                "extensions": [".py"],
                "dirs": [".venv", "venv", "env"],
            },
            "javascript": {
                "files": ["package.json", "yarn.lock"],
                "extensions": [".js", ".jsx"],
                "dirs": ["node_modules"],
            },
            "typescript": {
                "files": ["tsconfig.json", "package.json"],
                "extensions": [".ts", ".tsx"],
                "dirs": ["node_modules"],
            },
            "java": {
                "files": ["pom.xml", "build.gradle", "build.gradle.kts"],
                "extensions": [".java"],
                "dirs": [".gradle", "target"],
            },
            "kotlin": {
                "files": ["build.gradle.kts"],
                "extensions": [".kt", ".kts"],
                "dirs": [".gradle", "target"],
            },
            "flutter": {
                "files": ["pubspec.yaml", "pubspec.lock"],
                "extensions": [".dart"],
                "dirs": [".dart_tool", ".flutter-plugins"],
            },
            "go": {
                "files": ["go.mod", "go.sum"],
                "extensions": [".go"],
                "dirs": ["vendor"],
            },
            "rust": {
                "files": ["Cargo.toml", "Cargo.lock"],
                "extensions": [".rs"],
                "dirs": ["target"],
            },
            "ruby": {
                "files": ["Gemfile", "Gemfile.lock"],
                "extensions": [".rb"],
                "dirs": ["vendor/bundle"],
            },
            "php": {
                "files": ["composer.json", "composer.lock"],
                "extensions": [".php"],
                "dirs": ["vendor"],
            },
        }

    def detect_stacks(self, path: Path) -> Dict[str, List[str]]:
        """
        Detect tech stacks in folders recursively

        Args:
            path: Root path to analyze

        Returns:
            Dict mapping folder paths to lists of detected tech stacks
        """
        results = {}

        # First, find all project roots
        project_roots = self._find_project_roots(path)

        # For each project root, detect its tech stack
        for project_root in project_roots:
            relative_path = str(project_root.relative_to(path))
            tech_stacks = self._detect_stacks_in_folder(project_root)
            if tech_stacks:
                results[relative_path] = tech_stacks

        return results

    def _find_project_roots(self, path: Path) -> List[Path]:
        """
        Find project roots by looking for indicator files

        Args:
            path: Root path to search in

        Returns:
            List of project root paths
        """
        project_roots = []

        # Always include the root path as a potential project root
        project_roots.append(path)

        # Walk through directories to find project roots
        try:
            for item in path.rglob("*"):
                if item.is_dir() and not self._is_ignored(item):
                    # Check if this directory is a project root
                    if self._is_project_root(item):
                        # Only add if it's not already included or a subdirectory of an existing root
                        is_subdir = False
                        for existing_root in project_roots:
                            if (
                                item.is_relative_to(existing_root)
                                and item != existing_root
                            ):
                                is_subdir = True
                                break
                        if not is_subdir:
                            project_roots.append(item)
        except PermissionError:
            pass

        return project_roots

    def _is_project_root(self, folder_path: Path) -> bool:
        """
        Check if a folder is a project root by looking for indicator files

        Args:
            folder_path: Path to check

        Returns:
            True if the folder is a project root
        """
        try:
            # Get all files in the folder
            file_names = {item.name for item in folder_path.iterdir() if item.is_file()}

            # Check for project indicator files
            project_indicators = {
                "package.json",  # Node.js/JavaScript/TypeScript
                "pyproject.toml",
                "requirements.txt",
                "setup.py",
                "Pipfile",  # Python
                "pom.xml",
                "build.gradle",
                "build.gradle.kts",  # Java/Kotlin
                "pubspec.yaml",
                "pubspec.lock",  # Flutter/Dart
                "go.mod",
                "go.sum",  # Go
                "Cargo.toml",
                "Cargo.lock",  # Rust
                "Gemfile",
                "Gemfile.lock",  # Ruby
                "composer.json",
                "composer.lock",  # PHP
            }

            return bool(file_names & project_indicators)
        except PermissionError:
            return False

    def _is_ignored(self, path: Path) -> bool:
        """Check if path should be ignored"""
        ignored_names = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            "node_modules",
            ".venv",
            "venv",
            "build",
            "dist",
            "target",
            "vendor",
            ".eggs",
            ".tox",
            ".coverage",
        }

        # Ignore any path that contains site-packages (virtual environment packages)
        if "site-packages" in str(path):
            return True

        # Ignore any path that contains .venv or venv
        if any(venv_name in str(path) for venv_name in [".venv", "venv"]):
            return True

        return path.name in ignored_names

    def _detect_stacks_in_folder(self, folder_path: Path) -> List[str]:
        """Detect tech stacks in a single folder"""
        detected_stacks = []

        try:
            # Get all files and directories in the folder
            items = list(folder_path.iterdir())
            file_names = {item.name for item in items if item.is_file()}
            dir_names = {item.name for item in items if item.is_dir()}
            extensions = {item.suffix for item in items if item.is_file()}

            # Check each tech stack
            for stack, indicators in self.indicators.items():
                # Check for indicator files
                if any(
                    indicator_file in file_names
                    for indicator_file in indicators["files"]
                ):
                    detected_stacks.append(stack)
                    continue

                # Check for indicator directories
                if any(
                    indicator_dir in dir_names for indicator_dir in indicators["dirs"]
                ):
                    detected_stacks.append(stack)
                    continue

                # Check for file extensions
                if any(ext in extensions for ext in indicators["extensions"]):
                    detected_stacks.append(stack)
                    continue

        except PermissionError:
            pass

        return detected_stacks
