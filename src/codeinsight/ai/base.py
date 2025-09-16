"""
Base classes and interfaces for AI providers in Refactoroscope
"""

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AIProviderType(Enum):
    """Supported AI providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    QWEN = "qwen"


class CodeContext(BaseModel):
    """Context information for code analysis"""

    file_path: Path
    file_content: str
    language: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    related_files: List[Dict[str, Any]] = []
    project_structure: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None


class AIAnalysisResult(BaseModel):
    """Result of AI code analysis"""

    provider: str
    file_path: Path
    suggestions: List[Dict[str, Any]]
    confidence: float
    execution_time: float
    tokens_used: Optional[int] = None
    cost: Optional[float] = None


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    def __init__(
        self, api_key: Optional[str] = None, model: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Initialize the AI provider with credentials and settings"""
        pass

    @abstractmethod
    def analyze_code_quality(self, context: CodeContext) -> AIAnalysisResult:
        """Analyze code quality and provide suggestions"""
        pass

    @abstractmethod
    def analyze(self, prompt: str) -> str:
        """
        Analyze a prompt and return the AI's response as a string.

        Args:
            prompt: The prompt to analyze

        Returns:
            The AI's response as a string
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured and available"""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider name"""
        pass
