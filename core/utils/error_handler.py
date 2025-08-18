"""
Pentest-USB Toolkit - Error Handler
==================================

Comprehensive error handling and exception management
with recovery strategies and user-friendly messages.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import sys
import traceback
import logging
from typing import Optional, Dict, Any, Callable
from functools import wraps


class PentestError(Exception):
    """Base exception class for Pentest-USB Toolkit"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code or "PENTEST_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class NetworkError(PentestError):
    """Network-related errors"""
    
    def __init__(self, message: str, target: Optional[str] = None):
        super().__init__(message, "NETWORK_ERROR", {"target": target})


class ToolError(PentestError):
    """Tool execution errors"""
    
    def __init__(self, message: str, tool_name: Optional[str] = None, 
                 exit_code: Optional[int] = None):
        super().__init__(message, "TOOL_ERROR", {
            "tool_name": tool_name,
            "exit_code": exit_code
        })


class AuthenticationError(PentestError):
    """Authentication and authorization errors"""
    
    def __init__(self, message: str, service: Optional[str] = None):
        super().__init__(message, "AUTH_ERROR", {"service": service})


class ResourceError(PentestError):
    """System resource errors"""
    
    def __init__(self, message: str, resource_type: Optional[str] = None):
        super().__init__(message, "RESOURCE_ERROR", {"resource_type": resource_type})


class ConfigurationError(PentestError):
    """Configuration and setup errors"""
    
    def __init__(self, message: str, config_file: Optional[str] = None):
        super().__init__(message, "CONFIG_ERROR", {"config_file": config_file})


class ErrorHandler:
    """
    Centralized error handling and recovery system
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize error handler
        
        Args:
            logger: Logger instance for error reporting
        """
        from .logging_handler import get_logger
        self.logger = logger or get_logger(__name__)
        
        # Error recovery strategies
        self.recovery_strategies: Dict[str, Callable] = {
            "NETWORK_ERROR": self._handle_network_error,
            "TOOL_ERROR": self._handle_tool_error,
            "AUTH_ERROR": self._handle_auth_error,
            "RESOURCE_ERROR": self._handle_resource_error,
            "CONFIG_ERROR": self._handle_config_error
        }
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Handle an error with appropriate logging and recovery
        
        Args:
            error: Exception instance
            context: Additional context information
            
        Returns:
            bool: True if error was recovered, False otherwise
        """
        context = context or {}
        
        # Log the error
        self._log_error(error, context)
        
        # Try recovery strategy
        if isinstance(error, PentestError):
            recovery_func = self.recovery_strategies.get(error.error_code)
            if recovery_func:
                try:
                    return recovery_func(error, context)
                except Exception as recovery_error:
                    self.logger.error(f"Recovery strategy failed: {str(recovery_error)}")
        
        return False
    
    def _log_error(self, error: Exception, context: Dict[str, Any]):
        """Log error with full context"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc() if self.logger.isEnabledFor(logging.DEBUG) else None
        }
        
        if isinstance(error, PentestError):
            error_info.update({
                "error_code": error.error_code,
                "details": error.details
            })
        
        self.logger.error(f"Error occurred: {error_info}")
    
    def _handle_network_error(self, error: NetworkError, context: Dict[str, Any]) -> bool:
        """Handle network-related errors"""
        target = error.details.get("target")
        
        # Retry with different approach
        if "timeout" in error.message.lower():
            self.logger.info(f"Network timeout for {target}, will retry with longer timeout")
            return True
        
        if "connection refused" in error.message.lower():
            self.logger.info(f"Connection refused by {target}, target may be down")
            return False
        
        return False
    
    def _handle_tool_error(self, error: ToolError, context: Dict[str, Any]) -> bool:
        """Handle tool execution errors"""
        tool_name = error.details.get("tool_name")
        exit_code = error.details.get("exit_code")
        
        if exit_code == 1:
            self.logger.info(f"Tool {tool_name} returned exit code 1, may indicate no results")
            return True
        
        if "not found" in error.message.lower():
            self.logger.error(f"Tool {tool_name} not found, check installation")
            return False
        
        return False
    
    def _handle_auth_error(self, error: AuthenticationError, context: Dict[str, Any]) -> bool:
        """Handle authentication errors"""
        service = error.details.get("service")
        
        self.logger.warning(f"Authentication failed for {service}")
        
        # Could implement credential refresh logic here
        return False
    
    def _handle_resource_error(self, error: ResourceError, context: Dict[str, Any]) -> bool:
        """Handle resource constraint errors"""
        resource_type = error.details.get("resource_type")
        
        self.logger.warning(f"Resource constraint: {resource_type}")
        
        # Could implement resource cleanup or throttling here
        return False
    
    def _handle_config_error(self, error: ConfigurationError, context: Dict[str, Any]) -> bool:
        """Handle configuration errors"""
        config_file = error.details.get("config_file")
        
        self.logger.error(f"Configuration error in {config_file}")
        
        # Could implement default config fallback here
        return False


def error_handler(logger: Optional[logging.Logger] = None, 
                 reraise: bool = True,
                 return_on_error: Any = None):
    """
    Decorator for automatic error handling
    
    Args:
        logger: Logger instance
        reraise: Whether to reraise exceptions after handling
        return_on_error: Value to return if error occurs and reraise=False
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = ErrorHandler(logger)
                recovered = handler.handle_error(e, {
                    "function": func.__name__,
                    "args": str(args) if logger and logger.isEnabledFor(logging.DEBUG) else None,
                    "kwargs": str(kwargs) if logger and logger.isEnabledFor(logging.DEBUG) else None
                })
                
                if not recovered and reraise:
                    raise
                
                return return_on_error
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default=None, logger: Optional[logging.Logger] = None, **kwargs):
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        *args: Function arguments
        default: Default value to return on error
        logger: Logger instance
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default value on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if logger:
            logger.error(f"Safe execution failed for {func.__name__}: {str(e)}")
        return default