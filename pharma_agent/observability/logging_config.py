"""
Logging Configuration - Structured logging setup
Demonstrates: Observability, logging best practices
"""

import logging
import logging.handlers
import json
import sys
from datetime import datetime
from typing import Dict, Any
import os


class JsonFormatter(logging.Formatter):
    """Custom formatter for JSON structured logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data)


def setup_logging(
    log_level: str = None,
    log_format: str = None,
    log_file: str = None
):
    """
    Setup logging configuration for the agent.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_format: Format type ('json' or 'text')
        log_file: Path to log file
    """
    
    # Get configuration from environment or use defaults
    level = log_level or os.getenv("LOG_LEVEL", "INFO")
    format_type = log_format or os.getenv("LOG_FORMAT", "json")
    log_path = log_file or os.getenv("LOG_FILE", "./logs/agent.log")
    
    # Create logs directory if needed
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, level.upper()))
    
    # Set formatters
    if format_type == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    logging.info(f"Logging configured: level={level}, format={format_type}, file={log_path}")


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **context
):
    """
    Log message with additional context.
    
    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        **context: Additional context data
    """
    extra = {"extra_data": context}
    
    log_method = getattr(logger, level.lower())
    log_method(message, extra=extra)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)
