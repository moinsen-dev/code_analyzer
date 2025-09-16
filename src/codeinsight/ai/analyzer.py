"""
AI-powered code analyzer for Refactoroscope
"""

from pathlib import Path
from typing import List, Optional

from codeinsight.ai.base import AIAnalysisResult, CodeContext
from codeinsight.ai.factory import AIProviderFactory
from codeinsight.config.manager import ConfigManager
from codeinsight.models.metrics import Language


class AIAnalyzer:
    """AI-powered code analyzer"""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.providers = []

        # Initialize available providers
        available_providers = AIProviderFactory.get_available_providers(config_manager)
        for provider_type in available_providers:
            try:
                provider = AIProviderFactory.get_provider_instance(
                    provider_type, config_manager
                )
                self.providers.append(provider)
            except Exception as e:
                print(
                    f"Warning: Could not initialize {provider_type.value} provider: {e}"
                )

        if not self.providers:
            print("Warning: No AI providers available for analysis")

    def is_available(self) -> bool:
        """Check if any AI providers are available"""
        return len(self.providers) > 0

    def analyze_file(
        self, file_path: Path, language: Language
    ) -> List[AIAnalysisResult]:
        """Analyze a single file with all available AI providers"""
        if not self.is_available():
            return []

        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Create context
            context = CodeContext(
                file_path=file_path,
                file_content=content,
                language=language.value,
                project_structure=self._get_project_structure(file_path.parent),
            )

            # Analyze with all available providers
            results = []
            for provider in self.providers:
                try:
                    result = provider.analyze_code_quality(context)
                    results.append(result)
                except Exception as e:
                    print(
                        f"Warning: Error analyzing {file_path} with {provider.provider_name}: {e}"
                    )
                    continue

            return results

        except Exception as e:
            print(f"Warning: Could not read file {file_path} for AI analysis: {e}")
            return []

    def _get_project_structure(self, root_path: Path) -> dict:
        """Get a simplified project structure for context"""
        structure: dict = {"directories": [], "files": []}

        try:
            # Get top-level directories and files
            for item in root_path.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    structure["directories"].append(item.name)
                elif item.is_file():
                    structure["files"].append(
                        {"name": item.name, "extension": item.suffix}
                    )
        except Exception:
            # If we can't read the structure, return empty
            pass  # This is acceptable as we're just providing context info

        return structure

    def analyze(self, prompt: str) -> Optional[str]:
        """
        Analyze a general prompt and return the AI's response as a string.

        Args:
            prompt: The prompt to analyze

        Returns:
            The AI's response as a string or None if no provider is available
        """
        if not self.is_available():
            return None

        try:
            # Try providers in preference order
            preferences = self.get_provider_preferences()
            for provider_name in preferences:
                try:
                    # Find the provider
                    provider = None
                    for p in self.providers:
                        if p.provider_name == provider_name:
                            provider = p
                            break

                    if provider and provider.is_available():
                        result = provider.analyze(prompt)
                        return result
                except Exception:
                    # Try next provider
                    continue  # This is acceptable as we're trying multiple providers

            # If no preferred provider worked, use the first available
            for provider in self.providers:
                if provider.is_available():
                    result = provider.analyze(prompt)
                    return result

        except Exception as e:
            print(f"Warning: Could not analyze prompt with AI: {e}")

        return None

    def analyze_with_preferred_provider(
        self, file_path: Path, language: Language
    ) -> Optional[AIAnalysisResult]:
        """Analyze with the preferred provider based on configuration"""
        if not self.is_available():
            return None

        try:
            # Read file content
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Create context
            context = CodeContext(
                file_path=file_path,
                file_content=content,
                language=language.value,
                project_structure=self._get_project_structure(file_path.parent),
            )

            # Try providers in preference order
            preferences = self.get_provider_preferences()
            for provider_name in preferences:
                try:
                    # Find the provider
                    provider = None
                    for p in self.providers:
                        if p.provider_name == provider_name:
                            provider = p
                            break

                    if provider and provider.is_available():
                        result = provider.analyze_code_quality(context)
                        return result
                except Exception:
                    # Try next provider
                    continue  # This is acceptable as we're trying multiple providers

            # If no preferred provider worked, use the first available
            for provider in self.providers:
                if provider.is_available():
                    result = provider.analyze_code_quality(context)
                    return result

        except Exception as e:
            print(f"Warning: Could not analyze {file_path} with AI: {e}")

        return None

    def get_provider_preferences(self) -> List[str]:
        """Get provider preferences from configuration"""
        # Get configuration
        if hasattr(self.config_manager.config, "ai"):
            ai_config = self.config_manager.config.ai
            if ai_config is not None:
                return ai_config.provider_preferences
        # Default preference order
        return ["openai", "anthropic", "google", "ollama"]
