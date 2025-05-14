"""Profiling utilities for performance monitoring and optimization."""
import functools
import time
import logging
from typing import Any, Callable, Dict, Optional, TypeVar, cast

# Type variable for decorator
F = TypeVar('F', bound=Callable[..., Any])

# Setup logger
logger = logging.getLogger(__name__)

# Global registry for timing statistics
_timing_stats: Dict[str, Dict[str, float]] = {
    "count": {},     # Number of calls
    "total_time": {},  # Total execution time
    "min_time": {},    # Minimum execution time
    "max_time": {},    # Maximum execution time
}


def timed(func: F) -> F:
    """Decorator to time function execution.
    
    Logs the execution time and maintains statistics in the global registry.
    
    Args:
        func: The function to time
        
    Returns:
        The wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        func_name = f"{func.__module__}.{func.__qualname__}"
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Log the execution time
            logger.info(f"{func_name} executed in {execution_time:.4f} seconds")
            
            # Update statistics
            if func_name not in _timing_stats["count"]:
                _timing_stats["count"][func_name] = 0
                _timing_stats["total_time"][func_name] = 0.0
                _timing_stats["min_time"][func_name] = float('inf')
                _timing_stats["max_time"][func_name] = 0.0
                
            _timing_stats["count"][func_name] += 1
            _timing_stats["total_time"][func_name] += execution_time
            _timing_stats["min_time"][func_name] = min(
                _timing_stats["min_time"][func_name], execution_time
            )
            _timing_stats["max_time"][func_name] = max(
                _timing_stats["max_time"][func_name], execution_time
            )
            
    return cast(F, wrapper)


class Timer:
    """Context manager for timing code blocks.
    
    Example:
        with Timer("processing_video"):
            # Code to time
            process_video(video_path)
    """
    
    def __init__(self, name: str):
        """Initialize timer.
        
        Args:
            name: Name of the operation being timed
        """
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
    def __enter__(self) -> 'Timer':
        """Start timing when entering context.
        
        Returns:
            self: This Timer instance
        """
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """End timing when exiting context.
        
        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised
        """
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        
        # Log the execution time
        logger.info(f"{self.name} executed in {execution_time:.4f} seconds")
        
        # Update statistics
        if self.name not in _timing_stats["count"]:
            _timing_stats["count"][self.name] = 0
            _timing_stats["total_time"][self.name] = 0.0
            _timing_stats["min_time"][self.name] = float('inf')
            _timing_stats["max_time"][self.name] = 0.0
            
        _timing_stats["count"][self.name] += 1
        _timing_stats["total_time"][self.name] += execution_time
        _timing_stats["min_time"][self.name] = min(
            _timing_stats["min_time"][self.name], execution_time
        )
        _timing_stats["max_time"][self.name] = max(
            _timing_stats["max_time"][self.name], execution_time
        )


def get_timing_stats() -> Dict[str, Dict[str, Any]]:
    """Get the current timing statistics.
    
    Returns:
        Dict containing timing statistics with calculated averages
    """
    result = {
        "count": _timing_stats["count"].copy(),
        "total_time": _timing_stats["total_time"].copy(),
        "min_time": _timing_stats["min_time"].copy(),
        "max_time": _timing_stats["max_time"].copy(),
        "avg_time": {},
    }
    
    # Calculate average times
    for func_name in result["count"]:
        if result["count"][func_name] > 0:
            result["avg_time"][func_name] = (
                result["total_time"][func_name] / result["count"][func_name]
            )
        else:
            result["avg_time"][func_name] = 0.0
            
    return result


def reset_timing_stats() -> None:
    """Reset all timing statistics."""
    global _timing_stats
    _timing_stats = {
        "count": {},
        "total_time": {},
        "min_time": {},
        "max_time": {},
    }


def print_timing_report() -> None:
    """Print a report of all timing statistics."""
    stats = get_timing_stats()
    
    print("\n===== TIMING REPORT =====")
    print(f"{'Function/Operation':<50} {'Count':<8} {'Avg(s)':<10} {'Min(s)':<10} {'Max(s)':<10} {'Total(s)':<10}")
    print("-" * 100)
    
    # Sort by total time (descending)
    sorted_funcs = sorted(
        stats["count"].keys(),
        key=lambda x: stats["total_time"].get(x, 0),
        reverse=True
    )
    
    for func_name in sorted_funcs:
        count = stats["count"][func_name]
        avg_time = stats["avg_time"][func_name]
        min_time = stats["min_time"][func_name]
        max_time = stats["max_time"][func_name]
        total_time = stats["total_time"][func_name]
        
        print(f"{func_name:<50} {count:<8} {avg_time:<10.4f} {min_time:<10.4f} {max_time:<10.4f} {total_time:<10.4f}")
        
    print("=" * 100) 