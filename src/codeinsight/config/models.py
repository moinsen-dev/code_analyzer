"""
Configuration models for Refactoroscope
"""

from typing import Dict, List, Optional

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


class AIProviderConfig(BaseModel):
    """Configuration for an AI provider"""

    api_key: Optional[str] = Field(None, description="API key for the provider")
    model: Optional[str] = Field(None, description="Model to use for analysis")
    base_url: Optional[str] = Field(
        None, description="Base URL for the provider (for self-hosted models)"
    )
    enabled: bool = Field(True, description="Whether this provider is enabled")


class AIConfig(BaseModel):
    """AI configuration"""

    providers: Dict[str, AIProviderConfig] = Field(
        default_factory=dict, description="Configuration for different AI providers"
    )

    provider_preferences: List[str] = Field(
        default_factory=lambda: ["openai", "anthropic", "google", "ollama"],
        description="Preference order for AI providers",
    )

    enable_ai_suggestions: bool = Field(
        default=False, description="Whether to enable AI-powered suggestions"
    )

    max_file_size: int = Field(
        default=50000,  # 50KB
        description="Maximum file size to analyze with AI (in bytes)",
    )

    cache_results: bool = Field(
        default=True, description="Whether to cache AI analysis results"
    )

    cache_ttl: int = Field(
        default=3600, description="Cache time-to-live in seconds"  # 1 hour
    )


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
    ai: Optional[AIConfig] = Field(default=None, description="AI configuration")
