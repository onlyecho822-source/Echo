"""Logging configuration for Echo system."""

import logging
import os
from datetime import datetime
from typing import Optional


def get_logger(name: str, log_dir: Optional[str] = None) -> logging.Logger:
    """Get a configured logger for an Echo component."""

    logger = logging.getLogger(f"echo.{name}")

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler
    if log_dir is None:
        log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')

    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(
        log_dir,
        f"echo_{name}_{datetime.now().strftime('%Y%m%d')}.log"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    return logger
