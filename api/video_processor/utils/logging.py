"""
Logging configuration for the video processing application.

This module provides utilities for structured logging throughout
the application, with support for different environments and
log levels.
"""

import json
import logging
import logging.config
import os
import sys
from datetime import datetime
from typing import Any, Optional


class StructuredLogFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in a structured JSON format.
    Includes standard fields like timestamp, level, and message,
    plus any additional fields passed as extra args.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as a structured JSON object.

        Args:
            record: The log record to format

        Returns:
            A JSON string representation of the log record
        """
        # Basic log information
        log_data = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # If there's an exception, add traceback info
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add any additional attributes passed as extra
        for key, value in record.__dict__.items():
            if key not in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "id",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            } and not key.startswith("_"):
                log_data[key] = value

        return json.dumps(log_data)


class DevelopmentFormatter(logging.Formatter):
    """
    Formatter optimized for local development with colors and readability.
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m\033[37m",  # White on red background
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with colors for development.

        Args:
            record: The log record to format

        Returns:
            A formatted log string
        """
        level_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        # Format the timestamp
        timestamp = datetime.utcfromtimestamp(record.created).strftime("%H:%M:%S")

        # Basic log format with colors
        log_format = (
            f"{level_color}[{timestamp}] {record.levelname:<8}{reset} "
            f"{record.name:<20} | {record.getMessage()}"
        )

        # Add exception info if present
        if record.exc_info:
            log_format += f"\n{self.formatException(record.exc_info)}"

        # Add any additional context as a dictionary at the end
        extra_attrs = {}
        for key, value in record.__dict__.items():
            if key not in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "id",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            } and not key.startswith("_"):
                extra_attrs[key] = value

        if extra_attrs:
            log_format += f"\n{json.dumps(extra_attrs, indent=2)}"

        return log_format


def configure_logging(
    level: str = "INFO",
    environment: str = "development",
    log_file: Optional[str] = None,
) -> None:
    """
    Configure logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        environment: Environment type (development, production, test)
        log_file: Optional path to log file
    """
    # Default handlers write to stdout and file (if specified)
    handlers = ["console"]
    if log_file:
        handlers.append("file")

    # Basic logging config
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "()": StructuredLogFormatter,
            },
            "development": {
                "()": DevelopmentFormatter,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": (
                    "development" if environment == "development" else "structured"
                ),
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": handlers,
                "level": level,
                "propagate": True,
            },
            "video_processor": {
                "handlers": handlers,
                "level": level,
                "propagate": False,
            },
            # Third-party loggers
            "google": {
                "level": "WARNING",
            },
            "requests": {
                "level": "WARNING",
            },
        },
    }

    # Add file handler if log_file is specified
    if log_file:
        # Ensure the log directory exists
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)

        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "structured",  # Always use structured for files
            "filename": log_file,
            "maxBytes": 10485760,  # 10 MB
            "backupCount": 5,
            "encoding": "utf8",
        }

    # Configure logging with the defined config
    logging.config.dictConfig(config)

    # Log the configuration to confirm settings
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "level": level,
            "environment": environment,
            "log_file": log_file,
        },
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name, typically __name__ of the module

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Helper functions for structured logging


def log_event(logger: logging.Logger, event_name: str, **kwargs: Any) -> None:
    """
    Log a structured event with additional context.

    Args:
        logger: Logger instance
        event_name: Name of the event
        **kwargs: Additional context to include in the log
    """
    logger.info(f"Event: {event_name}", extra={"event": event_name, **kwargs})


def log_api_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    **kwargs: Any,
) -> None:
    """
    Log an API request with standardized fields.

    Args:
        logger: Logger instance
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
        **kwargs: Additional context to include in the log
    """
    logger.info(
        f"API {method} {path} {status_code} ({duration_ms:.2f}ms)",
        extra={
            "http_method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            **kwargs,
        },
    )
