"""Common code undeserving of its own module."""

import os
import logging
import contextlib
from functools import wraps

import typer

DEFAULT_PRETTY = False

DEFAULT_VERBOSE = 0


class TyperLoggerHandler(logging.Handler):
    """Logging handler that works well with typer."""

    def __init__(self, pretty: bool, *args, **kwargs):
        self.pretty = pretty
        super().__init__(*args, **kwargs)

    def emit(self, record: logging.LogRecord) -> None:
        if not self.pretty:
            typer.secho(self.format(record))
            return

        foreground = None
        background = None
        if record.levelno == logging.DEBUG:
            foreground = typer.colors.BLACK
            background = typer.colors.WHITE
        elif record.levelno == logging.INFO:
            foreground = typer.colors.BRIGHT_BLUE
        elif record.levelno == logging.WARNING:
            foreground = typer.colors.BRIGHT_MAGENTA
        elif record.levelno == logging.CRITICAL:
            foreground = typer.colors.BRIGHT_RED
        elif record.levelno == logging.ERROR:
            foreground = typer.colors.BLACK
            background = typer.colors.BRIGHT_RED
        typer.secho(self.format(record), bg=background, fg=foreground)


def config_logging(verbose: int = DEFAULT_VERBOSE, pretty: bool = DEFAULT_PRETTY):
    """Configure logging for stream and file."""

    level = logging.ERROR
    if verbose == 1:
        level = logging.INFO
    elif verbose > 1:
        level = logging.DEBUG

    logger = logging.getLogger()

    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    typer_handler = TyperLoggerHandler(pretty=pretty)
    typer_handler.setLevel(level)
    typer_handler.setFormatter(formatter)
    logger.addHandler(typer_handler)


def get_logger(name: str):
    """Create a new logger for name."""
    return logging.getLogger(name)


@contextlib.contextmanager
def temp_env(**environ):
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


def with_env(**environ):
    def actual_decorator(f):
        @wraps(f)
        def _decorator(*args, **kwargs):
            with temp_env(**environ):
                return f(*args, **kwargs)

        return _decorator

    return actual_decorator
