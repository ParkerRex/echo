"""
Factory for creating AI service adapters.

This module provides a factory function to get the appropriate AI adapter instance
based on the configuration settings.
"""

from typing import Optional

from apps.core.core.config import settings
from apps.core.lib.ai.base_adapter import AIAdapterInterface
from apps.core.lib.ai.gemini_adapter import GeminiAdapter


def get_ai_adapter(settings_instance=None) -> AIAdapterInterface:
    """
    Factory function to get the appropriate AI adapter based on settings.

    Args:
        settings_instance: Optional settings instance. If not provided, uses the global settings.

    Returns:
        An instance of a class implementing AIAdapterInterface

    Raises:
        ImportError: If the required AI service library is not installed
        ValueError: If the configuration is invalid or missing
    """
    settings_obj = settings_instance or settings

    # Determine which AI provider to use based on available API keys
    # If multiple API keys are available, prioritize in this order:
    # 1. Gemini (default)
    # 2. OpenAI
    # 3. Fall back to default (Gemini)

    if settings_obj.GEMINI_API_KEY:
        return GeminiAdapter(settings_obj)

    # Future implementations can add more AI adapters here
    # elif settings_obj.OPENAI_API_KEY:
    #     return OpenAIAdapter(settings_obj)

    # Default to Gemini (will raise an error if no API key is set)
    return GeminiAdapter(settings_obj)
