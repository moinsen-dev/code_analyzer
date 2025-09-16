"""
Factory for creating and managing AI providers in Refactoroscope
"""

import importlib
import os
from typing import Any, Dict, Optional, Type

from codeinsight.ai.base import AIProvider, AIProviderType
from codeinsight.config.manager import ConfigManager


class AIProviderFactory:
    """Factory for creating AI provider instances"""

    _providers: Dict[AIProviderType, Type[AIProvider]] = {}
    _instances: Dict[AIProviderType, AIProvider] = {}
    _providers_imported = False

    @classmethod
    def _import_all_providers(cls) -> None:
        """Dynamically import all provider modules to trigger registration"""
        if cls._providers_imported:
            return

        provider_modules = [
            "codeinsight.ai.openai_provider",
            "codeinsight.ai.anthropic_provider",
            "codeinsight.ai.google_provider",
            "codeinsight.ai.ollama_provider",
            "codeinsight.ai.qwen_provider",
        ]

        for module_name in provider_modules:
            try:
                importlib.import_module(module_name)
            except ImportError:
                # Provider not available (missing dependencies)
                pass

        cls._providers_imported = True

    @classmethod
    def register_provider(
        cls, provider_type: AIProviderType, provider_class: Type[AIProvider]
    ) -> None:
        """Register a new AI provider"""
        cls._providers[provider_type] = provider_class

    @classmethod
    def create_provider(
        cls, provider_type: AIProviderType, **kwargs: Any
    ) -> AIProvider:
        """Create an instance of an AI provider"""
        # Import all providers to ensure they're registered
        cls._import_all_providers()

        if provider_type not in cls._providers:
            raise ValueError(f"Provider {provider_type} is not registered")

        provider_class = cls._providers[provider_type]
        return provider_class(**kwargs)

    @classmethod
    def get_provider_instance(
        cls,
        provider_type: AIProviderType,
        config_manager: Optional[ConfigManager] = None,
    ) -> AIProvider:
        """Get a singleton instance of an AI provider"""
        # Import all providers to ensure they're registered
        cls._import_all_providers()

        if provider_type in cls._instances:
            return cls._instances[provider_type]

        # Get configuration
        if config_manager:
            config_ai = config_manager.config.ai
            if config_ai is not None:
                provider_config_obj = config_ai.providers.get(provider_type.value)
                if provider_config_obj is not None:
                    # Convert AIProviderConfig to dict
                    provider_config = {
                        "api_key": provider_config_obj.api_key,
                        "model": provider_config_obj.model,
                        "base_url": provider_config_obj.base_url,
                        "enabled": provider_config_obj.enabled,
                    }
                else:
                    provider_config = {}
            else:
                provider_config = {}
        else:
            provider_config = {}

        # Get API key from environment or config
        api_key = os.environ.get(
            f"{provider_type.value.upper()}_API_KEY"
        ) or provider_config.get("api_key")

        # Get model from config or use default
        model = provider_config.get("model")

        # Remove api_key and model from provider_config to avoid duplicate keyword arguments
        provider_config.pop("api_key", None)
        provider_config.pop("model", None)

        # Create provider instance
        provider = cls.create_provider(
            provider_type, api_key=api_key, model=model, **provider_config
        )
        cls._instances[provider_type] = provider

        return provider

    @classmethod
    def get_available_providers(
        cls, config_manager: Optional[ConfigManager] = None
    ) -> list:
        """Get list of available providers that are properly configured"""
        # Import all providers to ensure they're registered
        cls._import_all_providers()

        available = []
        for provider_type in cls._providers:
            try:
                provider = cls.get_provider_instance(provider_type, config_manager)
                if provider.is_available():
                    available.append(provider_type)
            except Exception:
                # Provider not available or misconfigured
                continue  # This is acceptable as we're checking multiple providers
        return available
