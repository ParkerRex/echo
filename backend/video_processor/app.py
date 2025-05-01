"""
Main application entry point.
"""
import os
import logging
from typing import Optional

from .api import create_app
from .config import get_settings
from .utils.logging import configure_logging

# Configure logging
logger = configure_logging(level=logging.INFO)
logger.info("🚀 app.py starting...")

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    logger.info("🏁 Attempting to run Flask development server...")
    try:
        settings = get_settings()
        app.run(host="0.0.0.0", port=settings.port, debug=settings.debug)
        logger.info(f"Flask server should be running on port {settings.port}")
    except Exception as e:
        logger.exception("❌ Failed to start Flask development server:")
        raise