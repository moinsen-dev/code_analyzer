"""
Configuration models for Refactoroscope
"""

from typing import Dict, List
from pydantic import BaseModel, Field


class LanguageConfig(BaseModel):
    """Language-specific configuration"""

    max_line_length: int = Field(default=88, description="Maximum line length")
    complexity_threshold: float = Field(
        default=10.0, description="Complexity threshold"
    )


class AnalysisConfig(BaseModel):
    """Analysis configuration"""

    ignore_patterns: List[str] = Field(
        default_factory=list, description="File patterns to ignore"
    )
    complexity: Dict[str, bool] = Field(
        default_factory=lambda: {"include_docstrings": False, "count_assertions": True},
        description="Complexity analysis options",
    )
    thresholds: Dict[str, int] = Field(
        default_factory=lambda: {
            "file_too_long": 500,
            "function_too_complex": 20,
            "class_too_large": 1000,
        },
        description="Analysis thresholds",
    )


class OutputConfig(BaseModel):
    """Output configuration"""

    format: str = Field(default="terminal", description="Output format")
    theme: str = Field(default="monokai", description="Output theme")
    show_recommendations: bool = Field(default=True, description="Show recommendations")
    export_path: str = Field(default="./reports", description="Export path")


class Config(BaseModel):
    """Main configuration model"""

    version: float = Field(default=1.0, description="Configuration version")
    languages: Dict[str, LanguageConfig] = Field(
        default_factory=dict, description="Language-specific settings"
    )
    analysis: AnalysisConfig = Field(
        default_factory=AnalysisConfig, description="Analysis rules"
    )
    output: OutputConfig = Field(
        default_factory=OutputConfig, description="Output preferences"
    )
