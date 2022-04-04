from __future__ import annotations

import logging
from collections.abc import MutableMapping
from logging import Logger


def get_logger(name: str, config: MutableMapping = None) -> Logger:
    """Obtaints a logger instance of the given name, optionally configured to
    have an output level of debug via toml config [main][verbose]
    Returns the logger instance"""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(name)
    if config and "verbose" in config["main"]:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    return logger
