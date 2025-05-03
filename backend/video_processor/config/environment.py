"""
Environment variable handling for the video processor.
"""

import os
from typing import Any, Optional


def get_env(key: str, default: Any = None, required: bool = False) -> Any:
    """
    Get an environment variable.

    Args:
        key: The environment variable name
        default: Default value if not found
        required: Whether the variable is required (raises error if missing)

    Returns:
        The environment variable value or default

    Raises:
        ValueError: If required is True and the variable is not set
    """
    value = os.environ.get(key)
    if value is None:
        if required:
            raise ValueError(f"Required environment variable {key} is not set")
        return default
    return value


def get_bool_env(key: str, default: bool = False) -> bool:
    """
    Get a boolean environment variable.

    Args:
        key: The environment variable name
        default: Default value if not found

    Returns:
        The boolean value (True for 'true', 'yes', '1', etc.)
    """
    value = get_env(key)
    if value is None:
        return default
    return value.lower() in ("true", "yes", "1", "y", "t")


def get_int_env(key: str, default: Optional[int] = None) -> Optional[int]:
    """
    Get an integer environment variable.

    Args:
        key: The environment variable name
        default: Default value if not found or not convertible

    Returns:
        The integer value or default
    """
    value = get_env(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default
