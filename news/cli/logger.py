import logging
from colorlog import ColoredFormatter

__all__ = 'enable', 'disable', 'info', 'warning', 'debug', 'error', 'critical'


# Logging handler and formatter
__NEWS_LOG_STREAM_HANDLER__ = logging.StreamHandler()
__NEWS_LOG_FORMATTER__ = ColoredFormatter(
    '%(asctime)s %(name)-4s %(levelname)-4s %(log_color)s%(message)s',
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
__NEWS_LOGGER__ = logging.getLogger()
__NEWS_LOGGER__.addHandler(__NEWS_LOG_STREAM_HANDLER__)

# Alias logging commands
def enable():
    __NEWS_LOGGER__.setLevel(logging.DEBUG)

def disable():
    __NEWS_LOGGER__.propagate = False

def info(l):
    __NEWS_LOGGER__.info(l)

def warning(l):
    __NEWS_LOGGER__.warning(l)

def debug(l):
    __NEWS_LOGGER__.debug(l)

def error(l):
    __NEWS_LOGGER__.error(l)

def critical(l):
    __NEWS_LOGGER__.critical(l)

# Defaults to logging enabled
enable()
