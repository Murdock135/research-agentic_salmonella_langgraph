"""Centralized logging configuration for the sparq package."""

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure logging for the sparq package.

    :param level: Logging level to use.
    :type level: int
    """
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    logger = logging.getLogger("sparq")
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    :param name: Module name (typically __name__).
    :type name: str
    :return: Logger instance.
    :rtype: logging.Logger
    """
    return logging.getLogger(name)