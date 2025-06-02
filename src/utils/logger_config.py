# src/utils/logger_config.py
import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from typing import Optional # Needs to be at the top for type hinting

LOG_DIR = "logs" # Directory to store log files
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except OSError as e:
        # Handle potential race condition if dir created between check and makedirs
        if not os.path.isdir(LOG_DIR):
            print(f"Error creating log directory {LOG_DIR}: {e}", file=sys.stderr)
            # Fallback or raise error if logging is critical
            # For now, will proceed and hope file handler creation fails gracefully or logs to console

DEFAULT_LOG_FILE = os.path.join(LOG_DIR, "simulation.log")
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s [%(levelname)s] - %(filename)s:%(lineno)d - %(message)s'
# Simpler format for console:
CONSOLE_LOG_FORMAT = '%(asctime)s - %(name)s [%(levelname)s] - %(message)s'


def setup_logging(log_level: int = DEFAULT_LOG_LEVEL,
                      log_file: str = DEFAULT_LOG_FILE,
                      log_format: str = DEFAULT_LOG_FORMAT,
                      console_log_level: Optional[int] = None, # Separate level for console
                      max_bytes: int = 10*1024*1024, # 10 MB
                      backup_count: int = 5):
    """
    Configures logging for the entire application.

    Args:
        log_level: The logging level for the root logger and file handler.
        log_file: Path to the log file.
        log_format: Format string for log messages in the file.
        console_log_level: Logging level for the console. Defaults to log_level if None.
        max_bytes: Maximum size of the log file before rotation.
        backup_count: Number of backup log files to keep.
    """
    logging.basicConfig(level=log_level, format=log_format, stream=sys.stdout) # Basic config for root

    root_logger = logging.getLogger()
    # Remove any existing handlers to avoid duplication if called multiple times
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # File Handler (Rotating)
    try:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Error setting up file logger to {log_file}: {e}", file=sys.stderr)


    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_log_level if console_log_level is not None else log_level)
    console_formatter = logging.Formatter(CONSOLE_LOG_FORMAT) # Use simpler format for console
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    logging.info("Logging setup complete. Logging to console and file: %s", log_file)
    
    # Example: Quieten overly verbose libraries if needed
    # logging.getLogger("matplotlib").setLevel(logging.WARNING)
    # logging.getLogger("networkx").setLevel(logging.INFO)


def get_project_logger(name: str) -> logging.Logger:
    """
    Returns a logger instance with the specified name, inheriting root config.
    """
    return logging.getLogger(name)


if __name__ == '__main__':
    # Example usage:
    setup_logging(log_level=logging.DEBUG, console_log_level=logging.INFO)
    
    logger1 = get_project_logger("my_module")
    logger2 = get_project_logger("another_module.sub_module")

    logger1.debug("This is a debug message from my_module.")
    logger1.info("This is an info message from my_module.")
    logger2.warning("This is a warning from another_module.")
    logger2.error("This is an error from another_module.")
    
    try:
        1 / 0
    except ZeroDivisionError:
        logger2.exception("A handled exception occurred!")
        
    print(f"Check '{DEFAULT_LOG_FILE}' for file logs.")

