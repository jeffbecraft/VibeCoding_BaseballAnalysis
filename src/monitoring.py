"""
Production Monitoring and Error Tracking
Integrates with Sentry for error monitoring and alerting.
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)

# Sentry integration (optional)
SENTRY_DSN = os.getenv('SENTRY_DSN')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

try:
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logger.info("Sentry SDK not installed. Error tracking disabled.")


def init_monitoring() -> bool:
    """
    Initialize production monitoring and error tracking.
    
    Returns:
        bool: True if monitoring was successfully initialized, False otherwise.
    """
    if not SENTRY_AVAILABLE:
        logger.info("Monitoring: Sentry not available (install: pip install sentry-sdk)")
        return False
    
    if not SENTRY_DSN:
        logger.info("Monitoring: SENTRY_DSN not configured. Error tracking disabled.")
        return False
    
    # Configure Sentry
    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENVIRONMENT,
        integrations=[sentry_logging],
        traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
        profiles_sample_rate=0.1,  # 10% for profiling
        send_default_pii=False,  # Don't send personally identifiable information
        attach_stacktrace=True,
        before_send=before_send_filter,
    )
    
    logger.info(f"Monitoring: Sentry initialized for environment: {ENVIRONMENT}")
    return True


def before_send_filter(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter events before sending to Sentry.
    
    Args:
        event: The error event
        hint: Additional context
        
    Returns:
        The event to send, or None to drop it
    """
    # Don't send events in development
    if ENVIRONMENT == 'development':
        return None
    
    # Filter out known non-critical errors
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        
        # Don't alert on expected errors
        if exc_type.__name__ in ['KeyboardInterrupt', 'SystemExit']:
            return None
    
    return event


def capture_exception(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Capture an exception and send to monitoring service.
    
    Args:
        error: The exception to capture
        context: Additional context about the error
    """
    if SENTRY_AVAILABLE and SENTRY_DSN:
        if context:
            sentry_sdk.set_context("error_context", context)
        sentry_sdk.capture_exception(error)
    else:
        logger.error(f"Exception occurred: {error}", exc_info=True)


def capture_message(message: str, level: str = 'info', context: Optional[Dict[str, Any]] = None) -> None:
    """
    Capture a message and send to monitoring service.
    
    Args:
        message: The message to capture
        level: Severity level (debug, info, warning, error, fatal)
        context: Additional context
    """
    if SENTRY_AVAILABLE and SENTRY_DSN:
        if context:
            sentry_sdk.set_context("message_context", context)
        sentry_sdk.capture_message(message, level=level)
    else:
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.log(log_level, message)


def set_user_context(user_id: Optional[str] = None, **kwargs) -> None:
    """
    Set user context for error tracking.
    
    Args:
        user_id: Optional user identifier
        **kwargs: Additional user attributes
    """
    if SENTRY_AVAILABLE and SENTRY_DSN:
        user_data = kwargs
        if user_id:
            user_data['id'] = user_id
        sentry_sdk.set_user(user_data)


def add_breadcrumb(message: str, category: str = 'default', level: str = 'info', data: Optional[Dict] = None) -> None:
    """
    Add a breadcrumb for debugging context.
    
    Args:
        message: Breadcrumb message
        category: Category (e.g., 'query', 'api', 'cache')
        level: Severity level
        data: Additional data
    """
    if SENTRY_AVAILABLE and SENTRY_DSN:
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data or {}
        )


class MonitoredOperation:
    """
    Context manager for monitoring operations.
    
    Example:
        with MonitoredOperation("fetch_player_stats", player_id=12345):
            stats = fetcher.get_player_stats(12345, 2024)
    """
    
    def __init__(self, operation_name: str, **context):
        self.operation_name = operation_name
        self.context = context
    
    def __enter__(self):
        add_breadcrumb(
            message=f"Starting: {self.operation_name}",
            category='operation',
            data=self.context
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            capture_exception(
                exc_val,
                context={
                    'operation': self.operation_name,
                    **self.context
                }
            )
        return False  # Don't suppress exceptions


# Performance monitoring decorator
def monitor_performance(operation_name: str):
    """
    Decorator to monitor function performance.
    
    Example:
        @monitor_performance('get_player_stats')
        def get_player_stats(player_id, season):
            # Your code here
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if SENTRY_AVAILABLE and SENTRY_DSN:
                with sentry_sdk.start_transaction(op=operation_name, name=func.__name__):
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Health check function
def get_monitoring_status() -> Dict[str, Any]:
    """
    Get current monitoring status.
    
    Returns:
        Dictionary with monitoring configuration
    """
    return {
        'sentry_available': SENTRY_AVAILABLE,
        'sentry_enabled': bool(SENTRY_DSN),
        'environment': ENVIRONMENT,
        'error_tracking': 'enabled' if (SENTRY_AVAILABLE and SENTRY_DSN) else 'disabled',
    }


if __name__ == '__main__':
    # Test monitoring setup
    print("Testing monitoring configuration...")
    
    status = get_monitoring_status()
    print(f"\nMonitoring Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    if init_monitoring():
        print("\n✅ Monitoring initialized successfully!")
        
        # Test error capture
        try:
            raise ValueError("Test error for monitoring")
        except Exception as e:
            capture_exception(e, context={'test': True})
            print("✅ Test error captured")
    else:
        print("\n⚠️  Monitoring not configured (optional)")
        print("   To enable: pip install sentry-sdk")
        print("   Set SENTRY_DSN in .env file")
