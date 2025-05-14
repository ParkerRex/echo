"""Monitoring and observability utilities for the video processor service."""
import json
import logging
import os
import time
import uuid
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast

# Type variables for decorator functions
F = TypeVar('F', bound=Callable[..., Any])

# Configure base logger
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create structured logger
logger = logging.getLogger("video_processor")

# Metrics registry
_metrics: Dict[str, Dict[str, float]] = {
    "counters": {},  # Simple counters
    "gauges": {},    # Point-in-time values
    "histograms": {}, # Distribution of values
}

# Request context for tracking request-specific data
_request_context: Dict[str, Any] = {}


class StructuredLogRecord(logging.LogRecord):
    """Extended LogRecord class that supports structured logging."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.structured_data = {}


class StructuredLogger(logging.Logger):
    """Logger that supports structured logging."""
    
    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, 
                  func=None, extra=None, sinfo=None):
        """Create a LogRecord with structured data support."""
        record = StructuredLogRecord(name, level, fn, lno, msg, args, exc_info, func, sinfo)
        if extra is not None:
            for key in extra:
                if key in ["message", "asctime", "levelname", "levelno"]:
                    raise KeyError(f"Attempt to overwrite {key} in StructuredLogRecord")
                record.__dict__[key] = extra[key]
        
        # Add request context data
        if _request_context:
            record.structured_data = {**_request_context}
            
        # Add structured data if provided in extra
        if extra and "structured_data" in extra:
            if isinstance(extra["structured_data"], dict):
                if hasattr(record, "structured_data"):
                    record.structured_data.update(extra["structured_data"])
                else:
                    record.structured_data = extra["structured_data"]
        
        return record


class StructuredJSONFormatter(logging.Formatter):
    """Formatter that outputs JSON strings for structured log records."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": super().format(record),
            "location": {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            },
        }
        
        # Add structured data if available
        if hasattr(record, "structured_data") and record.structured_data:
            log_data.update(record.structured_data)
            
        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }
            
        return json.dumps(log_data)


def setup_structured_logging(
    log_level: str = "INFO", 
    json_output: bool = False,
    log_file: Optional[str] = None,
) -> None:
    """Set up structured logging.
    
    Args:
        log_level: Logging level (default: INFO)
        json_output: Whether to output logs as JSON (default: False)
        log_file: Path to log file (default: None, logs to stdout)
    """
    # Register the StructuredLogger class
    logging.setLoggerClass(StructuredLogger)
    
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    if json_output:
        formatter = StructuredJSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Create handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Add handlers to root logger
    for handler in handlers:
        root_logger.addHandler(handler)
    
    # Set application logger
    app_logger = logging.getLogger("video_processor")
    app_logger.setLevel(getattr(logging, log_level))


def structured_log(level: str, message: str, structured_data: Dict[str, Any] = None) -> None:
    """Log a structured message.
    
    Args:
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        structured_data: Additional structured data to include
    """
    log_method = getattr(logger, level.lower())
    if structured_data:
        log_method(message, extra={"structured_data": structured_data})
    else:
        log_method(message)


def start_request_context(request_id: Optional[str] = None) -> str:
    """Start a new request context for request-specific logging.
    
    Args:
        request_id: Optional request ID (UUID generated if not provided)
        
    Returns:
        Request ID
    """
    global _request_context
    request_id = request_id or str(uuid.uuid4())
    _request_context = {
        "request_id": request_id,
        "start_time": time.time(),
    }
    return request_id


def add_request_context_data(data: Dict[str, Any]) -> None:
    """Add data to the current request context.
    
    Args:
        data: Data to add to the request context
    """
    global _request_context
    _request_context.update(data)


def end_request_context() -> None:
    """End the current request context."""
    global _request_context
    _request_context = {}


def log_request(log_request_body: bool = False, log_response_body: bool = False) -> Callable:
    """Decorator for logging requests and responses.
    
    Args:
        log_request_body: Whether to log request body (default: False)
        log_response_body: Whether to log response body (default: False)
        
    Returns:
        Decorator function
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request object
            request = None
            for arg in args:
                if hasattr(arg, "method") and hasattr(arg, "url"):
                    request = arg
                    break
            
            # Start request context
            request_id = start_request_context()
            
            if request:
                add_request_context_data({
                    "http_method": request.method,
                    "url_path": str(request.url),
                    "client_ip": request.client.host if hasattr(request, "client") else None,
                })
                
                # Log request
                log_data = {
                    "request_id": request_id,
                    "http_method": request.method,
                    "url_path": str(request.url),
                }
                
                if log_request_body and hasattr(request, "json"):
                    try:
                        log_data["request_body"] = await request.json()
                    except Exception:
                        pass
                        
                structured_log("info", f"Request received: {request.method} {request.url}", log_data)
                
                # Increment request counter
                increment_counter("http_requests_total")
                increment_counter(f"http_requests_{request.method.lower()}")
            
            # Process request
            start_time = time.time()
            try:
                response = await func(*args, **kwargs)
                
                # Log success response
                duration = time.time() - start_time
                status_code = response.status_code if hasattr(response, "status_code") else 200
                
                log_data = {
                    "request_id": request_id,
                    "status_code": status_code,
                    "duration_ms": round(duration * 1000, 2),
                }
                
                if log_response_body and hasattr(response, "body"):
                    try:
                        log_data["response_body"] = response.body.decode("utf-8")
                    except Exception:
                        pass
                
                structured_log(
                    "info", 
                    f"Request completed: {status_code} in {duration:.2f}s", 
                    log_data
                )
                
                # Record metrics
                observe_histogram("http_request_duration_seconds", duration)
                increment_counter(f"http_responses_{status_code}")
                
                return response
                
            except Exception as e:
                # Log error response
                duration = time.time() - start_time
                
                log_data = {
                    "request_id": request_id,
                    "exception": str(e),
                    "exception_type": e.__class__.__name__,
                    "duration_ms": round(duration * 1000, 2),
                }
                
                structured_log("error", f"Request failed: {e}", log_data)
                
                # Record metrics
                observe_histogram("http_request_duration_seconds", duration)
                increment_counter("http_responses_exception")
                
                # Re-raise exception
                raise
            finally:
                # End request context
                end_request_context()
        
        return cast(F, wrapper)
    
    return decorator


# Metrics functions
def increment_counter(name: str, value: float = 1.0) -> None:
    """Increment a counter metric.
    
    Args:
        name: Metric name
        value: Value to increment by (default: 1.0)
    """
    if name not in _metrics["counters"]:
        _metrics["counters"][name] = 0.0
    
    _metrics["counters"][name] += value


def set_gauge(name: str, value: float) -> None:
    """Set a gauge metric.
    
    Args:
        name: Metric name
        value: Value to set
    """
    _metrics["gauges"][name] = value


def observe_histogram(name: str, value: float) -> None:
    """Observe a value for a histogram metric.
    
    Args:
        name: Metric name
        value: Value to observe
    """
    if name not in _metrics["histograms"]:
        _metrics["histograms"][name] = []
    
    _metrics["histograms"][name].append(value)


def get_metrics() -> Dict[str, Dict[str, Any]]:
    """Get all metrics.
    
    Returns:
        Dictionary of metrics
    """
    result = {
        "counters": _metrics["counters"].copy(),
        "gauges": _metrics["gauges"].copy(),
        "histograms": {},
    }
    
    # Calculate histogram statistics
    for name, values in _metrics["histograms"].items():
        if not values:
            continue
            
        # Sort values for percentile calculation
        sorted_values = sorted(values)
        count = len(sorted_values)
        
        result["histograms"][name] = {
            "count": count,
            "sum": sum(sorted_values),
            "min": min(sorted_values),
            "max": max(sorted_values),
            "mean": sum(sorted_values) / count,
            "p50": sorted_values[int(count * 0.5)] if count > 0 else 0,
            "p90": sorted_values[int(count * 0.9)] if count > 0 else 0,
            "p95": sorted_values[int(count * 0.95)] if count > 0 else 0,
            "p99": sorted_values[int(count * 0.99)] if count > 0 else 0,
        }
    
    return result


def reset_metrics() -> None:
    """Reset all metrics."""
    global _metrics
    _metrics = {
        "counters": {},
        "gauges": {},
        "histograms": {},
    } 