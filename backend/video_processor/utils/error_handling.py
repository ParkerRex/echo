"""
Error handling utilities.
"""
import functools
import traceback
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union, cast

from .logging import get_logger

logger = get_logger(__name__)

# Type variables for better type hinting with decorators
F = TypeVar("F", bound=Callable[..., Any])
R = TypeVar("R")


class ProcessingError(Exception):
    """Base exception for video processing errors."""
    pass


class StorageError(ProcessingError):
    """Exception for storage-related errors."""
    pass


class TranscriptionError(ProcessingError):
    """Exception for transcription-related errors."""
    pass


class VideoProcessingError(ProcessingError):
    """Exception for video processing errors."""
    pass


class ConfigurationError(Exception):
    """Exception for configuration errors."""
    pass


def handle_exceptions(
    fallback_return: Optional[Any] = None,
    exception_types: Optional[Union[Type[Exception], tuple[Type[Exception], ...]]] = None,
    log_level: str = "error",
) -> Callable[[F], F]:
    """
    Decorator to handle exceptions in a function.
    
    Args:
        fallback_return: Value to return if an exception occurs
        exception_types: Exception types to catch (defaults to Exception)
        log_level: Logging level to use when an exception occurs
        
    Returns:
        Decorated function
    """
    if exception_types is None:
        exception_types = Exception
        
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                log_func = getattr(logger, log_level)
                log_func(
                    f"Error in {func.__name__}: {str(e)}\n"
                    f"{''.join(traceback.format_tb(e.__traceback__))}"
                )
                return fallback_return
                
        return cast(F, wrapper)
    return decorator


def retry(
    max_attempts: int = 3, 
    backoff_factor: float = 0.5,
    exception_types: Optional[Union[Type[Exception], tuple[Type[Exception], ...]]] = None,
) -> Callable[[F], F]:
    """
    Retry a function on failure with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        backoff_factor: Factor for exponential backoff
        exception_types: Exception types to catch and retry on
        
    Returns:
        Decorated function
    """
    if exception_types is None:
        exception_types = Exception
        
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            import time
            import random
            
            attempt = 0
            last_exception = None
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exception_types as e:
                    attempt += 1
                    last_exception = e
                    
                    if attempt >= max_attempts:
                        break
                        
                    # Calculate sleep time with jitter
                    sleep_time = backoff_factor * (2 ** (attempt - 1))
                    sleep_time = sleep_time + (random.random() * sleep_time * 0.5)
                    
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. "
                        f"Retrying in {sleep_time:.2f}s..."
                    )
                    time.sleep(sleep_time)
            
            # If we reach here, all attempts failed
            logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            raise last_exception
                
        return cast(F, wrapper)
    return decorator