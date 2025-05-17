"""
Unit tests for the AI client factory.
"""

from unittest.mock import patch

import pytest
from core.config import Settings

from apps.core.lib.ai.ai_client_factory import get_ai_adapter
from apps.core.lib.ai.base_adapter import AIAdapterInterface
from apps.core.lib.ai.gemini_adapter import GeminiAdapter


@pytest.fixture
def mock_settings_gemini():
    """Create mock settings with Gemini API key."""
    settings = Settings()
    settings.GEMINI_API_KEY = "fake-gemini-api-key"
    return settings


@pytest.fixture
def mock_settings_no_keys():
    """Create mock settings without any API keys."""
    settings = Settings()
    settings.GEMINI_API_KEY = None
    return settings


class TestAIClientFactory:
    """Test cases for the AI client factory."""

    def test_get_ai_adapter_with_gemini_key(self, mock_settings_gemini):
        """Test get_ai_adapter returns GeminiAdapter when Gemini API key is available."""
        with patch("apps.core.lib.ai.gemini_adapter.GeminiAdapter") as mock_gemini:
            # Configure the mock to return itself when called
            mock_gemini.return_value = mock_gemini

            # Call the factory function
            adapter = get_ai_adapter(mock_settings_gemini)

            # Verify GeminiAdapter was created with the settings
            mock_gemini.assert_called_once_with(mock_settings_gemini)

            # Verify correct adapter was returned
            assert adapter == mock_gemini

    def test_get_ai_adapter_with_no_keys(self, mock_settings_no_keys):
        """Test get_ai_adapter falls back to GeminiAdapter when no keys are available."""
        # This will raise an error since the GeminiAdapter requires an API key
        with pytest.raises(ValueError) as excinfo:
            get_ai_adapter(mock_settings_no_keys)

        assert "GEMINI_API_KEY must be set" in str(excinfo.value)

    @patch("core.config.settings")
    def test_get_ai_adapter_uses_global_settings(self, mock_global_settings):
        """Test get_ai_adapter uses global settings when none are provided."""
        # Configure the global settings mock
        mock_global_settings.GEMINI_API_KEY = "global-gemini-key"

        with patch("apps.core.lib.ai.gemini_adapter.GeminiAdapter") as mock_gemini:
            # Configure the mock to return itself when called
            mock_gemini.return_value = mock_gemini

            # Call the factory function without settings
            adapter = get_ai_adapter()

            # Verify GeminiAdapter was created with the global settings
            mock_gemini.assert_called_once_with(mock_global_settings)

            # Verify correct adapter was returned
            assert adapter == mock_gemini

    def test_get_ai_adapter_fallback_behavior(self):
        """Test the fallback behavior of get_ai_adapter."""
        custom_settings = Settings()
        custom_settings.GEMINI_API_KEY = "test-key"

        # Create a patch for GeminiAdapter that verifies it was called with our settings
        with patch("apps.core.lib.ai.gemini_adapter.GeminiAdapter") as mock_gemini:
            adapter = get_ai_adapter(custom_settings)
            mock_gemini.assert_called_once_with(custom_settings)
