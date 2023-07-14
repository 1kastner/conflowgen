import datetime
import logging
import os
import sys
from typing import Optional

from conflowgen.tools import docstring_parameter

LOGGING_DEFAULT_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        os.pardir,
        "data",
        "logs"
    )
)

# noinspection SpellCheckingInspection
DEFAULT_LOGGING_FORMAT_STRING: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


@docstring_parameter(DEFAULT_LOGGING_FORMAT_STRING=DEFAULT_LOGGING_FORMAT_STRING)
def setup_logger(
        logging_directory: Optional[str] = None,
        format_string: Optional[str] = None
) -> logging.Logger:
    """
    This sets up the default logger with the name 'conflowgen'.
    Several classes and functions use the same logger to inform the user about the current progress.
    This is just a convenience function, you can easily set up your own logger that uses the same name.
    See e.g.
    https://docs.python.org/3/howto/logging.html#configuring-logging
    for how to set up your own logger.

    Args:
        logging_directory:
            The path of the directory where to store logging files.
            Defaults to ``<project root>/data/logs/``.
        format_string:
            The format string to use.
            See e.g.
            https://docs.python.org/3/library/logging.html#logrecord-attributes
            for how to create your own format string.
            Defaults to ``{DEFAULT_LOGGING_FORMAT_STRING}``.

    Returns:
        The set-up logger instance.
    """
    if format_string is None:
        format_string = DEFAULT_LOGGING_FORMAT_STRING

    if logging_directory is None:
        logging_directory = LOGGING_DEFAULT_DIR

    time_prefix = str(datetime.datetime.now()).replace(":", "-").replace(" ", "--").split(".", maxsplit=1)[0]

    formatter = logging.Formatter(format_string, datefmt="%d.%m.%Y %H:%M:%S %z")

    logger = logging.getLogger("conflowgen")
    logger.setLevel(logging.DEBUG)

    stream_handlers = [handler for handler in logger.handlers if isinstance(handler, logging.StreamHandler)]
    if any(handler.stream == sys.stdout for handler in stream_handlers):
        logger.warning("Duplicate StreamHandler streaming to sys.stdout detected. "
                       "Skipping adding another StreamHandler.")
    else:
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if not os.path.isdir(logging_directory):
        logger.debug(f"Creating log directory at {logging_directory}")
        os.makedirs(logging_directory, exist_ok=True)
    path_to_log_file = os.path.join(
        logging_directory,
        time_prefix + ".log"
    )
    logger.debug(f"Creating log file at {path_to_log_file}")
    file_handler = logging.FileHandler(path_to_log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger
