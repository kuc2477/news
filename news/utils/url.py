import os.path
from urllib.parse import urlparse
import urltools


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
        filled = '{scheme}://{hostname}{path}{query}'.format(
            scheme=parsedu.scheme,
            hostname=parsedu.hostname,
            path=parsedu.path,
            query='?' + parsedu.query if parsedu.query else ''
        )

    # absoulte path
    elif isabspath(url):
        filled = '{scheme}://{hostname}{path}{query}'.format(
            scheme=parsedi.scheme,
            hostname=parsedi.hostname,
            path=parsedu.path,
            query='?' + parsedu.query if parsedu.query else ''
        )

    # relative path
    else:
        filled = '{index}/{path}'.format(
            index=parsedi.geturl(),
            path=parsedu.path
        )

    return normalize(filled)


def normalize(url):
    return urltools.normalize(url).rstrip('/')


def depth(index, url):
    if not issuburl(index, url):
        return -1

    nindex = normalize(index)
    nurl = normalize(fillurl(index, url))

    fragments = nurl.replace(nindex, '').split('/')

    if '' in fragments:
        fragments.remove('')

    return len(fragments)
