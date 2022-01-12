import datetime
import logging
import os
import sys
from typing import Optional


LOGGING_DEFAULT_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.pardir,
    "data",
    "logs"
)


DESIRED_LINE_LENGTH = 80  # doc: The console width used for wrapping output to new lines. This is not mandatory.


def setup_logger(
    logging_directory: Optional[str] = None
) -> logging.Logger:
    """
    This sets up the default logger with the name 'conflowgen'.
    Several classes and functions use the same logger to inform the user about the current progress.
    This is just a convenience function, you can easily set up your own logger that uses the same name.
    See e.g.
    https://docs.python.org/3/howto/logging.html#configuring-logging
    for how to set up your own logger.

    Args:
        logging_directory: The path of the directory where to store logging files.

    Returns:
        The set-up logger instance.
    """
    time_prefix = str(datetime.datetime.now()).replace(":", "-").replace(" ", "--").split(".", maxsplit=1)[0]
    # noinspection SpellCheckingInspection
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt="%d.%m.%Y %H:%M:%S %z"
    )

    logger = logging.getLogger("conflowgen")
    logger.setLevel(logging.DEBUG)

    flow_handler = logging.StreamHandler(stream=sys.stdout)
    flow_handler.setLevel(logging.DEBUG)
    flow_handler.setFormatter(formatter)
    logger.addHandler(flow_handler)

    if logging_directory is None:
        logging_directory = LOGGING_DEFAULT_DIR
    if not os.path.isdir(logging_directory):
        logger.debug(f"Creating log directory at '{logging_directory}'")
        os.makedirs(logging_directory, exist_ok=True)
    path_to_log_file = os.path.join(
        logging_directory,
        time_prefix + ".log"
    )
    logger.debug(f"Creating log file at '{path_to_log_file}'")
    file_handler = logging.FileHandler(path_to_log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger
