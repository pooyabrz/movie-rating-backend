import logging
import logging.config
import os
import sys
from typing import Dict, Any
from datetime import datetime
import uuid


class RequestIdFilter(logging.Filter):
    """Filter to add request_id to log records"""

    def __init__(self, request_id: str = None):
        super().__init__()
        self.request_id = request_id

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, 'request_id'):
            record.request_id = getattr(self, 'request_id', 'no-request-id')
        return True


class StructuredFormatter(logging.Formatter):
    """Structured JSON-like formatter for logs"""

    def format(self, record: logging.LogRecord) -> str:
        # Base log structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": os.getenv("SERVICE_NAME", "movie-rating-api"),
            "request_id": getattr(record, 'request_id', 'no-request-id'),
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, 'method'):
            log_entry["method"] = record.method
        if hasattr(record, 'path'):
            log_entry["path"] = record.path
        if hasattr(record, 'status_code'):
            log_entry["status_code"] = record.status_code
        if hasattr(record, 'duration_ms'):
            log_entry["duration_ms"] = record.duration_ms
        if hasattr(record, 'extra'):
            log_entry["extra"] = record.extra

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Format as readable string (not pure JSON for human readability)
        formatted = f"[{log_entry['timestamp']}] {log_entry['level']} {log_entry['service']} {log_entry['request_id']}"

        if 'method' in log_entry and 'path' in log_entry:
            formatted += f" {log_entry['method']} {log_entry['path']}"

        if 'status_code' in log_entry:
            formatted += f" {log_entry['status_code']}"

        if 'duration_ms' in log_entry:
            formatted += f" {log_entry['duration_ms']}ms"

        formatted += f" - {log_entry['message']}"

        if 'exception' in log_entry:
            formatted += f"\n{log_entry['exception']}"

        return formatted


def get_logger_config(log_level: str = "INFO") -> Dict[str, Any]:
    """Get logging configuration dictionary"""

    # Convert string log level to numeric
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "()": StructuredFormatter,
            },
        },
        "filters": {
            "request_id": {
                "()": RequestIdFilter,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": numeric_level,
                "formatter": "structured",
                "stream": sys.stdout,
                "filters": ["request_id"],
            },
            "file": {
                "class": "logging.FileHandler",
                "level": numeric_level,
                "formatter": "structured",
                "filename": "app.log",
                "filters": ["request_id"],
            },
        },
        "root": {
            "level": numeric_level,
            "handlers": ["console", "file"],
        },
        "loggers": {
            "app": {
                "level": numeric_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
        },
    }


def setup_logging() -> None:
    """Setup logging configuration"""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    config = get_logger_config(log_level)
    logging.config.dictConfig(config)


def get_logger(name: str = "app") -> logging.Logger:
    """Get configured logger instance"""
    return logging.getLogger(name)


# Global logger instance
logger = get_logger()