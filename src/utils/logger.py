"""
Flight Recorder: Centralized logging system for Founder OS MCP Server.

This module provides a configured logger that writes to both:
1. File: founder_os.log (in project root) - for persistent debugging
2. Console: stdout - for real-time visibility

Privacy Rules:
- DO NOT log full API keys or tokens
- DO NOT log full content of user documents (log metadata only)

CLI Design System Colors:
- Success: Green (SUCCESS, VERIFIED)
- Error/Block: Red (BLOCKED, VIOLATION)
- Info/Log: Dimmed Gray
- Highlight/Key: Purple (#b026ff) for "Founder OS" branding
- Warning: Yellow
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# ANSI Color Codes (CLI Design System)
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"    # Success
COLOR_RED = "\033[91m"      # Error/Block
COLOR_YELLOW = "\033[93m"   # Warning
COLOR_PURPLE = "\033[95m"   # Highlight/Key (Founder OS branding)
COLOR_GRAY = "\033[90m"     # Info/Log (Dimmed Gray)


def _sanitize_message(message: str) -> str:
    """
    Sanitize log messages to prevent accidental logging of sensitive data.
    
    Removes or masks API keys, tokens, and other sensitive information.
    """
    import re
    
    sanitized = message
    
    # Pattern 1: Mask API keys in environment variable format (NOTION_API_KEY=secret123)
    sanitized = re.sub(
        r'(NOTION_API_KEY|LINEAR_API_KEY)=([^\s]+)',
        r'\1=***',
        sanitized
    )
    
    # Pattern 2: Mask Authorization headers (Authorization: Bearer token123 or Authorization: token123)
    sanitized = re.sub(
        r'Authorization:\s*(Bearer\s+)?([^\s]+)',
        r'Authorization: ***',
        sanitized
    )
    
    # Pattern 3: Mask any remaining Bearer tokens
    sanitized = re.sub(
        r'Bearer\s+([^\s]+)',
        r'Bearer ***',
        sanitized
    )
    
    return sanitized


def setup_logger(name: str = "founder-os") -> logging.Logger:
    """
    Configure and return a logger instance for Founder OS.
    
    Args:
        name: Logger name (default: "founder-os")
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers if logger is already configured
    if logger.handlers:
        return logger
    
    # Disable propagation to root logger to prevent duplicate logs
    logger.propagate = False
    
    logger.setLevel(logging.INFO)

    # CLI Design System Formatter: [FounderOS] Message (with colors for console)
    class ColorFormatter(logging.Formatter):
        def format(self, record):
            # Base format with [FounderOS] prefix
            formatted_message = f"[FounderOS] {record.getMessage()}"

            # Add colors for console output (but not file output)
            if record.levelno >= logging.ERROR:
                formatted_message = f"{COLOR_RED}{formatted_message}{COLOR_RESET}"
            elif record.levelno >= logging.WARNING:
                formatted_message = f"{COLOR_YELLOW}{formatted_message}{COLOR_RESET}"
            elif record.levelno >= logging.INFO:
                formatted_message = f"{COLOR_GRAY}{formatted_message}{COLOR_RESET}"
            elif record.levelno >= logging.DEBUG:
                formatted_message = f"{COLOR_GRAY}{formatted_message}{COLOR_RESET}"

            # For branding/highlights, check for "Founder OS" in message
            if "Founder OS" in formatted_message or "FounderOS" in formatted_message:
                # Replace existing colors with purple for branding
                formatted_message = formatted_message.replace(COLOR_RED, COLOR_PURPLE)
                formatted_message = formatted_message.replace(COLOR_YELLOW, COLOR_PURPLE)
                formatted_message = formatted_message.replace(COLOR_GRAY, COLOR_PURPLE)
                formatted_message = formatted_message.replace(COLOR_GREEN, COLOR_PURPLE)

            return formatted_message

    formatter = ColorFormatter()
    
    # Handler 1: File output (founder_os.log in project root)
    # Get project root (where server.py is located)
    project_root = Path(__file__).parent.parent.parent
    log_file = project_root / "founder_os.log"
    
    # Rotating file handler: max 5MB per file, keep 3 backup files
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Handler 2: Console output (stderr - ONLY for WARNING+ levels to avoid MCP protocol conflicts)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING)  # Only WARNING, ERROR, CRITICAL to console
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Create module-level logger instance
logger = setup_logger()

# Add success method for green SUCCESS messages
def success(message, *args, **kwargs):
    """Log a success message in green."""
    formatted_msg = f"{COLOR_GREEN}{message}{COLOR_RESET}"
    logger.info(formatted_msg, *args, **kwargs)

# Add to logger instance
logger.success = success

# Suppress FastMCP and other third-party logging to prevent MCP protocol conflicts
logging.getLogger('mcp').setLevel(logging.WARNING)
logging.getLogger('mcp.server.fastmcp').setLevel(logging.WARNING)
logging.getLogger('mcp.server').setLevel(logging.WARNING)
logging.getLogger('starlette').setLevel(logging.WARNING)  # FastMCP uses Starlette
logging.getLogger('uvicorn').setLevel(logging.WARNING)    # FastMCP may use Uvicorn

# Override logger methods to sanitize messages
_original_info = logger.info
_original_error = logger.error
_original_warning = logger.warning
_original_debug = logger.debug
_original_exception = logger.exception
_original_success = logger.success


def _wrap_log_method(original_method):
    """Wrapper to sanitize log messages before logging."""
    def wrapper(message, *args, **kwargs):
        if isinstance(message, str):
            message = _sanitize_message(message)
        return original_method(message, *args, **kwargs)
    return wrapper

def _wrap_success_method(message, *args, **kwargs):
    """Wrapper for success method that sanitizes and preserves green color."""
    if isinstance(message, str):
        message = _sanitize_message(message)
    # Add green color after sanitization
    formatted_msg = f"{COLOR_GREEN}{message}{COLOR_RESET}"
    return _original_info(formatted_msg, *args, **kwargs)


logger.info = _wrap_log_method(_original_info)
logger.error = _wrap_log_method(_original_error)
logger.warning = _wrap_log_method(_original_warning)
logger.debug = _wrap_log_method(_original_debug)
logger.success = _wrap_success_method
logger.exception = lambda msg, *args, **kwargs: _original_exception(_sanitize_message(msg) if isinstance(msg, str) else msg, *args, **kwargs)

