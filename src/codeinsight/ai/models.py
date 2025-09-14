"""
AI configuration models for Refactoroscope
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


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
