"""
File watcher for real-time code analysis
"""

import time
from pathlib import Path
from typing import Callable, Optional, Set

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from codeinsight.models.metrics import AnalysisReport
from codeinsight.scanner import Scanner


class CodeChangeHandler(FileSystemEventHandler):
    """Handler for file system events that triggers code analysis"""

    def __init__(
        self,
        callback: Callable[[], None],
        project_path: Path,
        ignore_patterns: Optional[Set[str]] = None,
    ):
        self.callback = callback
        self.project_path = project_path
        self.ignore_patterns = ignore_patterns or set()
        self._scanner = Scanner(project_path)
        # Debouncing - to avoid multiple rapid analyses
        self._last_event_time = 0.0
        self._debounce_interval = 1.0  # 1 second debounce

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events"""
        if not event.is_directory and self._should_analyze(str(event.src_path)):
            self._debounced_callback()

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events"""
        if not event.is_directory and self._should_analyze(str(event.src_path)):
            self._debounced_callback()

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion events"""
        if not event.is_directory and self._should_analyze(str(event.src_path)):
            self._debounced_callback()

    def _debounced_callback(self) -> None:
        """Call the callback with debouncing to avoid too frequent updates"""
        current_time = time.time()
        if current_time - self._last_event_time > self._debounce_interval:
            self._last_event_time = current_time
            self.callback()

    def _should_analyze(self, file_path: str) -> bool:
        """Check if a file should trigger analysis"""
        path = Path(file_path)

        # Check if file is within project path
        try:
            path.relative_to(self.project_path)
        except ValueError:
            return False

        # Check ignore patterns
        for pattern in self.ignore_patterns:
            if pattern in str(path):
                return False

        # Use scanner's built-in filtering
        return self._scanner._should_analyze_file(path)


class CodeWatcher:
    """Main class for watching code changes and running analysis"""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.observer = Observer()
        self._scanner = Scanner(project_path)
        self._last_analysis: Optional[AnalysisReport] = None
        self._analysis_callback: Optional[Callable[[AnalysisReport], None]] = None

    def start(
        self,
        analysis_callback: Callable[[AnalysisReport], None],
        include_complexity: bool = False,
        enable_ai: bool = False,
        ignore_patterns: Optional[Set[str]] = None,
    ) -> None:
        """Start watching for file changes"""
        self._analysis_callback = analysis_callback
        ignore_patterns = ignore_patterns or set()

        # Add common patterns to ignore
        ignore_patterns.update(
            {
                "__pycache__",
                ".git",
                "node_modules",
                ".pytest_cache",
                ".mypy_cache",
                ".ruff_cache",
            }
        )

        event_handler = CodeChangeHandler(
            self._trigger_analysis, self.project_path, ignore_patterns
        )

        self.observer.schedule(event_handler, str(self.project_path), recursive=True)
        self.observer.start()

        # Run initial analysis
        self._run_analysis(include_complexity, enable_ai)

    def stop(self) -> None:
        """Stop watching for file changes"""
        self.observer.stop()
        self.observer.join()

    def _trigger_analysis(self) -> None:
        """Trigger analysis run"""
        if self._analysis_callback:
            # For now, we'll run a full analysis since our scanner is designed for full scans
            # In a more advanced implementation, we could optimize to only re-analyze changed files
            self._run_analysis()

    def _run_analysis(
        self, include_complexity: bool = False, enable_ai: bool = False
    ) -> None:
        """Run code analysis on the project"""
        try:
            # Create a new scanner with AI enabled if requested
            scanner = Scanner(self.project_path, enable_ai=enable_ai)
            report = scanner.analyze(
                self.project_path, include_complexity=include_complexity
            )
            self._last_analysis = report
            if self._analysis_callback:
                self._analysis_callback(report)
        except Exception as e:
            print(f"Error during analysis: {e}")
