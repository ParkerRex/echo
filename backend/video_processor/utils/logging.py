"""
Centralized logging configuration and utilities.
"""

import logging
import sys
from typing import Optional, Union


def configure_logging(
    level: Union[int, str] = logging.INFO,
    format_string: Optional[str] = None,
    logger_name: Optional[str] = None,
) -> logging.Logger:
    """
    Configure logging with consistent format across the application.

    Args:
        level: Logging level
        format_string: Custom format string (if None, uses default)
        logger_name: Name for the logger (if None, uses root logger)

    Returns:
        Logger instance
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Get logger by name or root logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates when called multiple times
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add console handler with formatting
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    Args:
        name: Logger name, typically __name__ from the calling module

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
