"""
Code scanner for analyzing directories and files
"""

import multiprocessing
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, List, Optional

from codeinsight.analysis.advanced_duplicates import advanced_duplicate_detector
from codeinsight.analysis.smells import CodeSmellDetector
from codeinsight.analyzers.complexity import ComplexityAnalyzer
from codeinsight.analyzers.line_counter import LineCounter
from codeinsight.analyzers.unused_code import UnusedCodeAnalyzer
from codeinsight.analyzers.unused_files import UnusedFileAnalyzer
from codeinsight.config.manager import ConfigManager
from codeinsight.models.metrics import (
    AnalysisReport,
    CodeInsights,
    FileMetrics,
    Language,
)
from codeinsight.utils.gitignore import GitIgnoreMatcher


class Scanner:
    """Main scanner class for analyzing codebases"""

    # Binary file extensions that should be ignored
    BINARY_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".bmp",
        ".ico",
        ".svg",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".zip",
        ".tar",
        ".gz",
        ".rar",
        ".7z",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".bin",
        ".mp3",
        ".mp4",
        ".avi",
        ".mov",
        ".wav",
        ".db",
        ".sqlite",
        ".mdb",
        ".jar",
        ".war",
        ".ear",
        ".class",
        ".o",
        ".obj",
        ".pyc",
        ".pyo",
    }

    # Directories that should always be ignored
    IGNORED_DIRECTORIES = {
        ".git",
        ".svn",
        ".hg",
        ".bzr",
        "node_modules",
        "vendor",
        "build",
        "dist",
        "__pycache__",
        ".pytest_cache",
        ".coverage",
        "coverage",
        "target",
        "bin",
        "obj",
    }

    # File patterns that should be ignored (generated files, lock files, etc.)
    IGNORED_FILE_PATTERNS = {
        # Generated files
        "*.g.dart",
        "*.freezed.dart",
        "*.generated.*",
        "*_generated.*",
        # Lock files
        "*.lock",
        "*.lock.yaml",  # Generic lock files
        "pubspec.lock",
        "package-lock.json",
        "*-lock.json",
        "yarn.lock",
        "Gemfile.lock",
        "composer.lock",
        "Cargo.lock",
        "poetry.lock",
        "Pipfile.lock",
        "conda-lock.yml",
        "mix.lock",
        # Build/Project files
        "*.pbxproj",
        "*.xcodeproj",
        "*.xcworkspace",
        "*.xib",
        "*.storyboard",
        "*.nib",
        "*.lproj",
        # IDE files
        "*.iml",
        ".idea",
        ".vscode",
        "*.swp",
        "*.swo",
        # Log files
        "*.log",
        "log.txt",
        # Temp/cache files
        "*.tmp",
        "*.temp",
        ".DS_Store",
        "Thumbs.db",
        # Minified files
        "*.min.js",
        "*.min.css",
        # Backup files
        "*~",
        "*.bak",
        "*.backup",
        # Coverage reports
        "coverage.xml",
        "lcov.info",
        "*.cobertura.xml",
    }

    # Maximum file size to analyze (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def __init__(
        self,
        project_path: Optional[Path] = None,
        enable_duplicates: bool = True,
        enable_ai: bool = False,
    ):
        self.project_path = project_path or Path.cwd()
        self.enable_duplicates = enable_duplicates
        self.enable_ai = enable_ai
        self.config_manager = ConfigManager(self.project_path)
        self.gitignore_matcher = GitIgnoreMatcher()
        self.line_counter = LineCounter()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.unused_code_analyzer = UnusedCodeAnalyzer()
        self.unused_file_analyzer = UnusedFileAnalyzer()
        self.smell_detector = CodeSmellDetector()

        # Initialize AI analyzer if enabled
        self.ai_analyzer = None
        if self.enable_ai:
            try:
                from codeinsight.ai.analyzer import AIAnalyzer

                self.ai_analyzer = AIAnalyzer(self.config_manager)
            except ImportError:
                # AI functionality not available
                self.ai_analyzer = None

    # Directories that should always be ignored
    IGNORED_DIRECTORIES = {
        ".git",
        ".svn",
        ".hg",
        ".bzr",
        "node_modules",
        "vendor",
        "build",
        "dist",
        "__pycache__",
        ".pytest_cache",
        ".coverage",
        "coverage",
        "target",
        "bin",
        "obj",
    }

    # File patterns that should be ignored (generated files, lock files, etc.)
    IGNORED_FILE_PATTERNS = {
        # Generated files
        "*.g.dart",
        "*.freezed.dart",
        "*.generated.*",
        "*_generated.*",
        # Lock files
        "*.lock",
        "*.lock.yaml",  # Generic lock files
        "pubspec.lock",
        "package-lock.json",
        "*-lock.json",
        "yarn.lock",
        "Gemfile.lock",
        "composer.lock",
        "Cargo.lock",
        "poetry.lock",
        "Pipfile.lock",
        "conda-lock.yml",
        "mix.lock",
        # Build/Project files
        "*.pbxproj",
        "*.xcodeproj",
        "*.xcworkspace",
        "*.xib",
        "*.storyboard",
        "*.nib",
        "*.lproj",
        # IDE files
        "*.iml",
        ".idea",
        ".vscode",
        "*.swp",
        "*.swo",
        # Log files
        "*.log",
        "log.txt",
        # Temp/cache files
        "*.tmp",
        "*.temp",
        ".DS_Store",
        "Thumbs.db",
        # Minified files
        "*.min.js",
        "*.min.css",
        # Backup files
        "*~",
        "*.bak",
        "*.backup",
        # Coverage reports
        "coverage.xml",
        "lcov.info",
        "*.cobertura.xml",
    }

    def analyze(self, path: Path, include_complexity: bool = False) -> AnalysisReport:
        """
        Analyze a directory path and return an analysis report

        Args:
            path: Path to analyze
            include_complexity: Whether to include complexity analysis

        Returns:
            AnalysisReport with findings
        """
        if not path.exists():
            raise FileNotFoundError(f"Path {path} does not exist")

        if path.is_file():
            # If a single file is provided, get its directory
            path = path.parent

        # Find all files
        files = self._discover_files(path)

        # Analyze each file using parallel processing
        insights = []
        total_lines = 0
        total_size = 0
        language_dist: Dict[Language, int] = {}

        # Use parallel processing for better performance on large codebases
        max_workers = min(multiprocessing.cpu_count(), 8)  # Limit to 8 workers max

        # Process files in batches to avoid memory issues
        batch_size = 100
        for i in range(0, len(files), batch_size):
            batch = files[i : i + batch_size]

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all file analysis tasks
                future_to_file = {
                    executor.submit(
                        self._analyze_file_parallel, file_path, path, include_complexity
                    ): file_path
                    for file_path in batch
                }

                # Collect results as they complete
                for future in as_completed(future_to_file):
                    try:
                        result = future.result()
                        if result:
                            insight, file_metrics = result

                            # Update totals
                            total_lines += file_metrics.lines_of_code
                            total_size += file_metrics.size_bytes

                            # Update language distribution
                            lang = file_metrics.language
                            language_dist[lang] = language_dist.get(lang, 0) + 1

                            insights.append(insight)
                    except Exception as e:
                        file_path = future_to_file[future]
                        print(f"Warning: Could not analyze {file_path}: {e}")
                        continue

        # Sort by lines of code (descending)
        insights.sort(key=lambda x: x.file_metrics.lines_of_code, reverse=True)

        # Create report
        report = AnalysisReport(
            project_path=path,
            timestamp=datetime.now(),
            total_files=len(insights),
            total_lines=total_lines,
            total_size=total_size,
            language_distribution=language_dist,
            top_files=insights,
        )

        # Add unused file analysis at the project level
        unused_files = self.unused_file_analyzer.analyze(path, self.config_manager)

        # Add unused files to report recommendations
        if unused_files:
            report.recommendations.extend(
                [
                    f"Unused file detected: {finding.path} (confidence: {finding.confidence:.0%}) - {finding.reason}"
                    for finding in unused_files
                ]
            )

        return report

    def _analyze_file_parallel(
        self, file_path: Path, root_path: Path, include_complexity: bool
    ) -> tuple[CodeInsights, FileMetrics] | None:
        """
        Analyze a single file in parallel processing context

        Args:
            file_path: Path to the file
            root_path: Root directory for relative path calculation
            include_complexity: Whether to include complexity analysis

        Returns:
            Tuple of (CodeInsights, FileMetrics) or None if analysis failed
        """
        try:
            # Get file metrics
            file_metrics = self._analyze_file(file_path, root_path)

            # Create insights object
            insight = CodeInsights(file_metrics=file_metrics)

            # Add complexity analysis if requested
            if include_complexity:
                complexity = self.complexity_analyzer.analyze(
                    file_path, file_metrics.language
                )
                if complexity:
                    insight.complexity_metrics = complexity

            # Add code smells
            smells = self.smell_detector.detect_smells(file_path, file_metrics.language)
            if smells:
                insight.code_smells = smells

            # Add code duplications if enabled
            if self.enable_duplicates:
                basic_duplications = self.smell_detector.detect_duplications(
                    file_path, file_metrics.language
                )

                # Add advanced duplicate detection
                advanced_duplications = advanced_duplicate_detector.detect_duplicates(
                    file_path, file_metrics.language
                )

                # Combine both types of duplications
                all_duplications = basic_duplications + advanced_duplications
                if all_duplications:
                    insight.duplications = all_duplications

            # Add unused code analysis
            unused_code = self.unused_code_analyzer.analyze(
                file_path, file_metrics.language
            )
            if unused_code:
                insight.unused_code = unused_code

            # Add AI analysis if enabled and available
            if self.enable_ai and self.ai_analyzer and self.ai_analyzer.is_available():
                # Only analyze files that are not too large
                if file_path.stat().st_size <= 50000:  # 50KB limit
                    try:
                        ai_result = self.ai_analyzer.analyze_with_preferred_provider(
                            file_path, file_metrics.language
                        )
                        if ai_result and ai_result.suggestions:
                            # Convert AI suggestions to code smells for display
                            ai_smells = [
                                f"AI Suggestion: {suggestion.get('description', 'No description')}"
                                for suggestion in ai_result.suggestions
                            ]
                            insight.code_smells.extend(ai_smells)
                    except Exception:
                        # Don't fail the entire analysis if AI analysis fails
                        pass  # Acceptable as we don't want AI failures to break the whole analysis

            return (insight, file_metrics)
        except Exception as e:
            raise e

    def _discover_files(self, root_path: Path) -> List[Path]:
        """
        Discover all files in a directory, respecting .gitignore rules and config patterns

        Args:
            root_path: Root directory to scan

        Returns:
            List of file paths
        """
        files = []

        for dirpath, dirnames, filenames in os.walk(root_path):
            dir_path = Path(dirpath)

            # Skip ignored directories
            if self._should_ignore_directory(dir_path):
                dirnames[:] = []  # Don't traverse this directory
                continue

            # Update gitignore matcher for this directory
            self.gitignore_matcher.update_for_directory(dir_path)

            # Filter directories (don't traverse ignored directories)
            filtered_dirnames = []
            for d in dirnames:
                dir_full_path = dir_path / d
                if not self._should_ignore_directory(dir_full_path):
                    gitignore_matches = self.gitignore_matcher.matches_directory(
                        dir_full_path
                    )
                    config_matches = self.config_manager.should_ignore_file(
                        dir_full_path
                    )
                    if not gitignore_matches and not config_matches:
                        filtered_dirnames.append(d)
            dirnames[:] = filtered_dirnames

            # Add files that aren't ignored
            for filename in filenames:
                file_path = dir_path / filename
                if self._should_analyze_file(file_path):
                    gitignore_matches = self.gitignore_matcher.matches_file(file_path)
                    config_matches = self.config_manager.should_ignore_file(file_path)
                    if not gitignore_matches and not config_matches:
                        files.append(file_path)

        return files

    def _should_ignore_directory(self, dir_path: Path) -> bool:
        """
        Check if a directory should be ignored

        Args:
            dir_path: Path to directory

        Returns:
            True if directory should be ignored
        """
        # Check if it's a special ignored directory
        if dir_path.name in self.IGNORED_DIRECTORIES:
            return True

        # Check if it's outside the project path
        try:
            dir_path.relative_to(self.project_path)
        except ValueError:
            return True

        return False

    def _should_analyze_file(self, file_path: Path) -> bool:
        """
        Check if a file should be analyzed

        Args:
            file_path: Path to file

        Returns:
            True if file should be analyzed
        """
        # Skip binary files
        if file_path.suffix.lower() in self.BINARY_EXTENSIONS:
            return False

        # Skip files that are too large
        try:
            if file_path.stat().st_size > self.MAX_FILE_SIZE:
                return False
        except OSError:
            # If we can't stat the file, skip it
            return False

        # Skip files in ignored directories
        if self._should_ignore_directory(file_path.parent):
            return False

        # Skip files matching ignored patterns
        file_name = file_path.name
        file_path_str = str(file_path.relative_to(self.project_path)).replace("\\", "/")

        for pattern in self.IGNORED_FILE_PATTERNS:
            if fnmatch(file_name, pattern) or fnmatch(file_path_str, pattern):
                return False

        # Special handling for JSON files - ignore most but allow some
        if file_path.suffix.lower() == ".json":
            # Allow package.json as it's often considered source code
            if file_name == "package.json":
                return True
            # Ignore all other JSON files
            return False

        # Special handling for YAML files - ignore lock files but allow others
        if file_path.suffix.lower() in [".yaml", ".yml"]:
            # Ignore lock.yaml files
            if "lock.yaml" in file_name or "lock.yml" in file_name:
                return False
            # Allow other YAML files (they might be config files but could be relevant)
            return True

        return True

    def _analyze_file(self, file_path: Path, root_path: Path) -> FileMetrics:
        """
        Analyze a single file and return its metrics

        Args:
            file_path: Path to the file
            root_path: Root directory (for relative path calculation)

        Returns:
            FileMetrics for the file
        """
        # Get file stats
        stat = file_path.stat()

        # Determine language
        language = self._detect_language(file_path)

        # Count lines
        loc, blank, comment = self.line_counter.count_lines(file_path, language)

        # Calculate relative path
        try:
            relative_path = file_path.relative_to(root_path)
        except ValueError:
            relative_path = file_path

        return FileMetrics(
            path=file_path,
            relative_path=str(relative_path),
            language=language,
            lines_of_code=loc,
            blank_lines=blank,
            comment_lines=comment,
            size_bytes=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
        )

    def _detect_language(self, file_path: Path) -> Language:
        """
        Detect the programming language of a file based on extension

        Args:
            file_path: Path to the file

        Returns:
            Detected Language
        """
        extension = file_path.suffix.lower()

        extension_map = {
            ".py": Language.PYTHON,
            ".js": Language.JAVASCRIPT,
            ".ts": Language.TYPESCRIPT,
            ".jsx": Language.JAVASCRIPT,
            ".tsx": Language.TYPESCRIPT,
            ".java": Language.JAVA,
            ".cs": Language.CSHARP,
            ".cpp": Language.CPP,
            ".cc": Language.CPP,
            ".cxx": Language.CPP,
            ".c": Language.CPP,
            ".go": Language.GO,
            ".rs": Language.RUST,
            ".dart": Language.DART,
            ".swift": Language.SWIFT,
            ".kt": Language.KOTLIN,
            ".php": Language.PHP,
            ".rb": Language.RUBY,
            ".html": Language.HTML,
            ".htm": Language.HTML,
            ".css": Language.CSS,
            ".scss": Language.CSS,
            ".sql": Language.SQL,
            ".yml": Language.YAML,
            ".yaml": Language.YAML,
            ".json": Language.JSON,
            ".md": Language.MARKDOWN,
            ".xml": Language.MARKDOWN,  # Treat XML as markdown for now
            ".toml": Language.MARKDOWN,  # Treat TOML as markdown for now
            ".cfg": Language.MARKDOWN,  # Treat config files as markdown for now
            ".ini": Language.MARKDOWN,  # Treat INI files as markdown for now
            ".txt": Language.MARKDOWN,  # Treat text files as markdown for now
        }

        return extension_map.get(extension, Language.MARKDOWN)  # Default to markdown
