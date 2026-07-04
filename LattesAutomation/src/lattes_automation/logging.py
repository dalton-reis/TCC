"""Configuração centralizada de logs."""

from pathlib import Path

from loguru import logger


def configure_logging(log_directory: Path, verbose: bool = False) -> None:
    """Configura saída no terminal e arquivo rotativo."""
    log_directory.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(
        lambda message: print(message, end=""),
        level="DEBUG" if verbose else "INFO",
        colorize=True,
    )
    logger.add(
        log_directory / "lattes_automation_{time:YYYY-MM-DD}.log",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        encoding="utf-8",
    )
