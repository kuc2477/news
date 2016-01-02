import re
import os.path
import logging
from urllib.parse import urlparse

from colorlog import ColoredFormatter


def ispath(url):
    parsed = urlparse(url)
    return not parsed.scheme and not parsed.hostname

def isabspath(url):
    parsed = urlparse(url)
    return ispath(url) and url.startswith('/')

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

    if not ispath(url):
        return parsedu.geturl()

    elif isabspath(url):
        return '%s://%s/%s%s' % (
            parsedi.scheme, parsedi.hostname, parsedu.path,
            '?' + parsedu.query if parsedu.query else ''
        )

    else:
        return '%s/%s' % (parsedi.geturl(), url)

def normalize(url):
    parsed = urlparse(url)
    normpath = re.sub(r'\/+', '/', os.path.normpath('/' + parsed.path))
    normpath = '' if normpath == '/' else normpath
    query = '?' + parsed.query if parsed.query else ''
    return '%s://%s%s%s' % (
        parsed.scheme, parsed.hostname, normpath, query
    )

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

def _enable_logger():
    __NEWS_LOGGER__.propagate = True
    __NEWS_LOGGER__.setLevel(logging.DEBUG)

def _disable_logger():
    __NEWS_LOGGER__.propagate = False

# Export logger alias
logger = __NEWS_LOGGER__
logger.enable = _enable_logger
logger.disable = _disable_logger
