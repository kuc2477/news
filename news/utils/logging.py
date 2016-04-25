import logging

from timeit import default_timer
from contextlib import contextmanager
from functools import partial

from colorlog import ColoredFormatter


# Execution time measuring context manager for logging purpose
@contextmanager
def elapsed_timer():
    start = default_timer()

    def elapser():
        return default_timer() - start

    yield lambda: elapser()


# Logging handler and formatter
__NEWS_LOG_STREAM_HANDLER__ = logging.StreamHandler()
__NEWS_LOG_FORMATTER__ = ColoredFormatter(
    '%(asctime)s %(name)-4s %(log_color)s%(message)s',
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white'
    },
    secondary_log_colors={},
    style='%'
)

# Configure handler with formatter
__NEWS_LOG_STREAM_HANDLER__.setFormatter(__NEWS_LOG_FORMATTER__)

# Configure logger
__NEWS_LOGGER__ = logging.getLogger('NEWS')
__NEWS_LOGGER__.addHandler(__NEWS_LOG_STREAM_HANDLER__)

# Export logger alias
logger = __NEWS_LOGGER__
logger.enable = lambda: logger.setLevel('DEBUG')
logger.disable = lambda: logger.setLevel('CRITICAL')
logger.enable()
