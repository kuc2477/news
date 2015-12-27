import os.path
import logging
from colorlog import ColoredFormatter
from urllib.parse import urlparse


def ispath(url):
    parsed = urlparse(url)
    return not parsed.scheme and not parsed.hostname

def issamehost(index, url):
    return ispath(url) or urlparse(index).hostname == urlparse(url).hostname

def issuburl(index, url):
    parsedi = urlparse(index)
    parsedu = urlparse(url)
    return issamehost(index, url) and parsedu.path.startswith(parsedi.path)

def ext(url):
    return os.path.splitext(url)[1][1:]

def fillurl(index, url):
    parsedi = urlparse(index)
    parsedu = urlparse(url)
    return '%s://%s/%s' % (parsedi.scheme, parsedi.hostname, parsedu.path) if \
        ispath(url) else parsedu.geturl()


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
__NEWS_LOGGER__ = logging.getLogger('NEWS')
__NEWS_LOGGER__.addHandler(__NEWS_LOG_STREAM_HANDLER__)

def _enable():
    __NEWS_LOGGER__.setLevel(logging.DEBUG)

def _disable():
    __NEWS_LOGGER__.propagate = False

# Export logger alias
logger = __NEWS_LOGGER__
logger.enable = _enable
logger.disable = _disable

# Defaults to logging disabled
logger.disable()
