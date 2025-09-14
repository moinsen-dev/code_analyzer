"""
Factory for creating and managing AI providers in Refactoroscope
"""

import os
from typing import Dict, Type
from codeinsight.ai.base import AIProvider, AIProviderType
from codeinsight.config.manager import ConfigManager


class AIProviderFactory:
    """Factory for creating AI provider instances"""

    _providers: Dict[AIProviderType, Type[AIProvider]] = {}
    _instances: Dict[AIProviderType, AIProvider] = {}

    @classmethod
    def register_provider(
        cls, provider_type: AIProviderType, provider_class: Type[AIProvider]
    ):
        """Register a new AI provider"""
        cls._providers[provider_type] = provider_class

    @classmethod
    def create_provider(cls, provider_type: AIProviderType, **kwargs) -> AIProvider:
        """Create an instance of an AI provider"""
        if provider_type not in cls._providers:
            raise ValueError(f"Provider {provider_type} is not registered")

        provider_class = cls._providers[provider_type]
        return provider_class(**kwargs)

    @classmethod
    def get_provider_instance(
        cls, provider_type: AIProviderType, config_manager: ConfigManager = None
    ) -> AIProvider:
        """Get a singleton instance of an AI provider"""
        if provider_type in cls._instances:
            return cls._instances[provider_type]

        # Get configuration
        if config_manager:
            ai_config = (
                config_manager.config.ai if hasattr(config_manager.config, "ai") else {}
            )
            provider_config = ai_config.get(provider_type.value, {})
        else:
            provider_config = {}

        # Get API key from environment or config
        api_key = os.environ.get(
            f"{provider_type.value.upper()}_API_KEY"
        ) or provider_config.get("api_key")

        # Get model from config or use default
        model = provider_config.get("model")

        # Create provider instance
        provider = cls.create_provider(
            provider_type, api_key=api_key, model=model, **provider_config
        )
        cls._instances[provider_type] = provider

        return provider

    @classmethod
    def get_available_providers(cls, config_manager: ConfigManager = None) -> list:
        """Get list of available providers that are properly configured"""
        available = []
        for provider_type in cls._providers:
            try:
                provider = cls.get_provider_instance(provider_type, config_manager)
                if provider.is_available():
                    available.append(provider_type)
            except Exception:
                # Provider not available or misconfigured
                continue
        return available
