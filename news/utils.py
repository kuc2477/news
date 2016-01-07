import re
import os.path
import logging

from timeit import default_timer
from contextlib import contextmanager
from functools import partial
from urllib.parse import urlparse

from colorlog import ColoredFormatter


def ispath(url):
    parsed = urlparse(url)
    return not parsed.scheme and not parsed.hostname

def isabspath(url):
    parsed = urlparse(url)
    return ispath(url) and url.startswith('/')

def isrelpath(url):
    parsed = urlparse(url)
    return ispath(url) and not url.startswith('/')

def issamehost(index, url):
    return ispath(url) or urlparse(index).hostname == urlparse(url).hostname

def issuburl(index, url):
    parsedi = urlparse(index)
    parsedu = urlparse(url)
    return issamehost(index, url) and  (
        isrelpath(url) or
        parsedu.path.rstrip('/').startswith(
        parsedi.path.rstrip('/'))
    )

def ext(url):
    return os.path.splitext(url)[1][1:]

def fillurl(index, url):
    parsedi = urlparse(index)
    parsedu = urlparse(url)

    if not ispath(url):
        filled = parsedu.geturl()

    elif isabspath(url):
        filled = '%s://%s/%s%s' % (
            parsedi.scheme, parsedi.hostname, parsedu.path.lstrip('/'),
            '?' + parsedu.query if parsedu.query else ''
        )

    else:
        filled = '%s/%s' % (parsedi.geturl(), url)

    return normalize(filled)

def normalize(url):
    parsed = urlparse(url)
    normpath = re.sub(r'\/+', '/', os.path.normpath('/' + parsed.path))
    normpath = '' if normpath == '/' else normpath
    query = '?' + parsed.query if parsed.query else ''
    return '%s://%s%s%s' % (
        parsed.scheme, parsed.hostname, normpath, query
    )

def depth(index, url):
    if not issuburl(index, url):
        return -1

    nindex = normalize(index)
    nurl = normalize(fillurl(index, url))

    fragments = nurl.replace(nindex, '').split('/')

    if '' in fragments:
        fragments.remove('')

    return len(fragments)


# Execution time measuring context manager for logging purpose
@contextmanager
def elapsed_timer():
    start = default_timer()
    elapser = lambda: default_timer() - start
    yield lambda: elapser()
    end = default_timer()
    elapser = lambda: end - start


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

def _set_mode(self, silent):
    if not silent:
        self.propagate = True
        self.setLevel(logging.DEBUG)
    else:
        self.propagate = False

# Export logger alias
logger = __NEWS_LOGGER__
logger.set_mode = partial(_set_mode, logger)
