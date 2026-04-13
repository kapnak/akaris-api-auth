import sys
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""

    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',  # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        # Store original levelname
        original_levelname = record.levelname

        # Format the message with the original levelname
        formatted = super().format(record)

        # Apply color to the output string only
        log_color = self.COLORS.get(original_levelname, self.RESET)
        formatted = formatted.replace(
            original_levelname,
            f"{log_color}{original_levelname:8s}{self.RESET}",
            1  # Only replace the first occurrence
        )

        return formatted


def setup_logging(
        app_name: str = __name__,
        log_level: str = "INFO",
        log_dir: Optional[str] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        json_logs: bool = True,
        console_logs: bool = True,
) -> logging.Logger:
    """
    Setup logging configuration

    Args:
        app_name: Name of the application (used for logger name)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files (optional)
        max_bytes: Maximum size of each log file before rotation
        backup_count: Number of backup files to keep
        json_logs: Enable JSON formatted file logging
        console_logs: Enable console logging

    Returns:
        Configured logger instance
    """

    log_level = log_level.upper()

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console Handler with colored output
    if console_logs:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_formatter = ColoredFormatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File Handlers
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

        # File Handler - Standard format
        file_handler = RotatingFileHandler(
            log_path / f"{app_name}.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        # JSON File Handler - Structured logging
        if json_logs:
            json_handler = RotatingFileHandler(
                log_path / f"{app_name}_json.log",
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8"
            )
            json_handler.setLevel(log_level)
            json_handler.setFormatter(JSONFormatter())
            root_logger.addHandler(json_handler)

        # Error File Handler - Only errors and critical
        error_handler = RotatingFileHandler(
            log_path / f"{app_name}_error.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)

    # Configure uvicorn loggers
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers.clear()
    uvicorn_access.propagate = True

    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.handlers.clear()
    uvicorn_error.propagate = True

    # Configure FastAPI logger
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.handlers.clear()
    fastapi_logger.propagate = True

    # Get application logger
    app_logger = logging.getLogger(app_name)

    app_logger.info(f"Logging initialized for {app_name}")
    app_logger.info(f"Log level: {log_level}")
    if log_dir:
        app_logger.info(f"Log directory: {Path(log_dir).absolute()}")
    else:
        app_logger.info("File logging disabled (no log directory provided)")

    return app_logger
