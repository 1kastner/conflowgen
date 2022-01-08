import datetime
import logging
import os
import sys

logs_root_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.pardir,
    "data",
    "logs"
)


DESIRED_LINE_LENGTH = 80  # doc: The console width used for wrapping output to new lines. This is not mandatory.


def setup_logger() -> logging.Logger:
    """
    This sets up the default logger with the name 'conflowgen'.
    Several classes and functions use the same logger to inform the user about the current progress.
    This is just a convenience function, you can easily set up your own logger that uses the same name.
    See e.g.
    https://docs.python.org/3/howto/logging.html#configuring-logging
    for how to set up your own logger.

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

    file_handler = logging.FileHandler(
        os.path.join(
            logs_root_dir,
            time_prefix + ".log"
        )
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger
