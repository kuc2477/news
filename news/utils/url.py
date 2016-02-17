import re
import os.path
from urllib.parse import urlparse


def ispath(url):
    parsed = urlparse(url)
    return not parsed.scheme and not parsed.hostname


def isabspath(url):
    return ispath(url) and url.startswith('/')


def isrelpath(url):
    return ispath(url) and not url.startswith('/')


def issamehost(index, url):
    return ispath(url) or urlparse(index).hostname == urlparse(url).hostname


def issuburl(index, url):
    parsedi = urlparse(index)
    parsedu = urlparse(url)
    return issamehost(index, url) and (
        isrelpath(url) or
        parsedu.path.rstrip('/').startswith(parsedi.path.rstrip('/'))
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
