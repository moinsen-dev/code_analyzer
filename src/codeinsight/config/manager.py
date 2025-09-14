"""
Configuration manager for Refactoroscope
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from codeinsight.config.models import AIConfig, Config, LanguageConfig


class ConfigManager:
    """Manages configuration loading and defaults"""

    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path or Path.cwd()
        self.config: Config = self._load_config()

    def _load_config(self) -> Config:
        """Load configuration from .refactoroscope.yml file or use defaults"""
        config_path = self.project_path / ".refactoroscope.yml"

        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config_data = yaml.safe_load(f)
                return Config(**config_data)
            except Exception as e:
                print(f"Warning: Could not load config file {config_path}: {e}")
                # Fall back to defaults
                pass

        # Return default configuration
        return self._get_default_config()

    def _get_default_config(self) -> Config:
        """Get default configuration"""
        config = Config()

        # Set up default language configurations
        config.languages = {
            "python": LanguageConfig(max_line_length=88, complexity_threshold=10),
            "typescript": LanguageConfig(max_line_length=100, complexity_threshold=15),
            "javascript": LanguageConfig(max_line_length=100, complexity_threshold=15),
        }

        # Set up default AI configuration
        config.ai = AIConfig(
            providers={},
            provider_preferences=["openai", "anthropic", "google", "ollama"],
            enable_ai_suggestions=False,
            max_file_size=50000,
            cache_results=True,
            cache_ttl=3600,
        )

        return config

    def get_language_config(self, language: str) -> LanguageConfig | Dict[str, Any]:
        """Get configuration for a specific language"""
        return self.config.languages.get(language, {})

    def get_analysis_thresholds(self) -> Dict[str, int]:
        """Get analysis thresholds"""
        return self.config.analysis.thresholds

    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration"""
        return {
            "format": self.config.output.format,
            "theme": self.config.output.theme,
            "show_recommendations": self.config.output.show_recommendations,
            "export_path": self.config.output.export_path,
        }

    def should_ignore_file(self, file_path: Path) -> bool:
        """Check if a file should be ignored based on patterns"""
        from fnmatch import fnmatch

        # Get relative path from project root
        try:
            relative_path = file_path.relative_to(self.project_path)
            path_str = str(relative_path).replace(
                "\\", "/"
            )  # Normalize path separators
        except ValueError:
            # File is not under project path, use just the filename
            path_str = file_path.name

        # Check each pattern
        for pattern in self.config.analysis.ignore_patterns:
            pattern = pattern.replace("\\", "/")  # Normalize pattern separators
            if fnmatch(path_str, pattern) or fnmatch(file_path.name, pattern):
                return True

        return False
