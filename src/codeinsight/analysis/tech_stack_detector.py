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

        # Walk through directories
        for folder_path in self._get_folders(path):
            tech_stacks = self._detect_stacks_in_folder(folder_path)
            if tech_stacks:
                results[str(folder_path.relative_to(path))] = tech_stacks

        return results

    def _get_folders(self, path: Path) -> List[Path]:
        """Get all folders in the path recursively"""
        folders = [path]
        try:
            for item in path.rglob("*"):
                if item.is_dir() and not self._is_ignored(item):
                    folders.append(item)
        except PermissionError:
            pass
        return folders

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
        }
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
