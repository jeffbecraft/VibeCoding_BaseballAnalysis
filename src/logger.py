"""
Structured Logging Module

Provides centralized logging configuration for the MLB Statistics Analysis System.

BENEFITS:
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Timestamps and context automatically included
- Easy to disable/enable in production
- Can log to files, console, or external services
- Better than print() statements for debugging and monitoring

USAGE:
```python
from logger import get_logger

logger = get_logger(__name__)
logger.info("Fetching player stats...")
logger.warning("Cache miss, calling API")
logger.error("API request failed", exc_info=True)
```
"""

import logging
import sys
import os
from typing import Optional


def get_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Get or create a logger with consistent formatting.
    
    Args:
        name: Logger name (typically __name__ from calling module)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               If None, uses LOG_LEVEL env var or defaults to INFO
        log_file: Optional file path to write logs to
        
    Returns:
        Configured logger instance
        
    EXAMPLE:
    ```python
    logger = get_logger(__name__)
    logger.info("Processing data...")  # Shows: 2025-11-30 10:30:15 - module_name - INFO - Processing data...
    ```
    """
    # Get log level from environment variable or parameter
    if level is None:
        level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level, logging.INFO))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatter with timestamp, module name, level, and message
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def set_log_level(level: str) -> None:
    """
    Change log level for all loggers in the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    USAGE:
    ```python
    set_log_level('DEBUG')  # Enable verbose debugging
    set_log_level('WARNING')  # Only show warnings and errors
    ```
    """
    logging.root.setLevel(getattr(logging, level.upper(), logging.INFO))
    for handler in logging.root.handlers:
        handler.setLevel(getattr(logging, level.upper(), logging.INFO))


# Pre-configured loggers for common modules
def get_api_logger() -> logging.Logger:
    """Get logger for API-related operations."""
    return get_logger('mlb_stats.api')


def get_cache_logger() -> logging.Logger:
    """Get logger for cache operations."""
    return get_logger('mlb_stats.cache')


def get_ai_logger() -> logging.Logger:
    """Get logger for AI operations."""
    return get_logger('mlb_stats.ai')
