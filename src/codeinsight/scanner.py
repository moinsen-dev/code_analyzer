"""
Code scanner for analyzing directories and files
"""
import os
from pathlib import Path
from typing import List, Set
from datetime import datetime

from codeinsight.models.metrics import (
    FileMetrics, CodeInsights, AnalysisReport, Language
)
from codeinsight.utils.gitignore import GitIgnoreMatcher
from codeinsight.analyzers.line_counter import LineCounter
from codeinsight.analyzers.complexity import ComplexityAnalyzer
from codeinsight.analysis.smells import CodeSmellDetector
from codeinsight.config.manager import ConfigManager


class Scanner:
    """Main scanner class for analyzing codebases"""
    
    def __init__(self, project_path: Path = None):
        self.project_path = project_path or Path.cwd()
        self.config_manager = ConfigManager(self.project_path)
        self.gitignore_matcher = GitIgnoreMatcher()
        self.line_counter = LineCounter()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.smell_detector = CodeSmellDetector()
    
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
        
        # Analyze each file
        insights = []
        total_lines = 0
        total_size = 0
        language_dist = {}
        
        for file_path in files:
            try:
                # Get file metrics
                file_metrics = self._analyze_file(file_path, path)
                
                # Update totals
                total_lines += file_metrics.lines_of_code
                total_size += file_metrics.size_bytes
                
                # Update language distribution
                lang = file_metrics.language
                language_dist[lang] = language_dist.get(lang, 0) + 1
                
                # Create insights object
                insight = CodeInsights(file_metrics=file_metrics)
                
                # Add complexity analysis if requested
                if include_complexity:
                    complexity = self.complexity_analyzer.analyze(file_path, lang)
                    if complexity:
                        insight.complexity_metrics = complexity
                
                # Add code smells
                smells = self.smell_detector.detect_smells(file_path, lang)
                if smells:
                    insight.code_smells = smells
                
                insights.append(insight)
                
            except Exception as e:
                # Skip files that cause errors
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
            top_files=insights
        )
        
        return report
    
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
            
            # Update gitignore matcher for this directory
            self.gitignore_matcher.update_for_directory(dir_path)
            
            # Filter directories (don't traverse ignored directories)
            filtered_dirnames = []
            for d in dirnames:
                dir_full_path = dir_path / d
                gitignore_matches = self.gitignore_matcher.matches_directory(dir_full_path)
                config_matches = self.config_manager.should_ignore_file(dir_full_path)
                if not gitignore_matches and not config_matches:
                    filtered_dirnames.append(d)
            dirnames[:] = filtered_dirnames
            
            # Add files that aren't ignored
            for filename in filenames:
                file_path = dir_path / filename
                gitignore_matches = self.gitignore_matcher.matches_file(file_path)
                config_matches = self.config_manager.should_ignore_file(file_path)
                if not gitignore_matches and not config_matches:
                    files.append(file_path)
        
        return files
    
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
            last_modified=datetime.fromtimestamp(stat.st_mtime)
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
            '.py': Language.PYTHON,
            '.js': Language.JAVASCRIPT,
            '.ts': Language.TYPESCRIPT,
            '.jsx': Language.JAVASCRIPT,
            '.tsx': Language.TYPESCRIPT,
            '.java': Language.JAVA,
            '.cs': Language.CSHARP,
            '.cpp': Language.CPP,
            '.cc': Language.CPP,
            '.cxx': Language.CPP,
            '.c': Language.CPP,
            '.go': Language.GO,
            '.rs': Language.RUST,
            '.dart': Language.DART,
            '.swift': Language.SWIFT,
            '.kt': Language.KOTLIN,
            '.php': Language.PHP,
            '.rb': Language.RUBY,
            '.html': Language.HTML,
            '.htm': Language.HTML,
            '.css': Language.CSS,
            '.scss': Language.CSS,
            '.sql': Language.SQL,
            '.yml': Language.YAML,
            '.yaml': Language.YAML,
            '.json': Language.JSON,
            '.md': Language.MARKDOWN,
        }
        
        return extension_map.get(extension, Language.MARKDOWN)  # Default to markdown