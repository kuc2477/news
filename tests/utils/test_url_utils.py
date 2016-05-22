from urllib.parse import urlparse
import pytest
from news.utils import url


@pytest.fixture(params=[
    'http://www.index.com/a'
])
def index(request):
    return request.param


@pytest.fixture(params=[
    'http://www.index.com/a/b',
    'http://www.index.com/a',
    '/a',
    '/a/b'
])
def suburl(request):
    return request.param


@pytest.fixture(params=[
    'http://www.index.com/b',
    'http://www.index.com/b/c/',
    'http://www.index.com/b/d',
    '/b/c',
    '/b',
    '/b/',
    '/'
])
def nonsuburl(request):
    return request.param


@pytest.fixture(params=[
    '/a/b/c',
    '/a/../cd/b',
    '/a'
])
def abspath(request):
    return request.param


@pytest.fixture(params=[
    'b/c',
    'b/c/d',
    '../a/c'
])
def relpath(request):
    return request.param


@pytest.fixture(params=[
    'http://www.somewhere/a/b',
    'https://www.somewhere2/b/c/d/'
])
def exturl(request):
    return request.param


@pytest.fixture(params=[
    'http://www.index.com/a/b/c',
    'http://www.index.com/a/b/c/d'
])
def nonpath(request):
    return request.param


def test_ispath(relpath, abspath, exturl, nonpath):
    assert(url.ispath(relpath))
    assert(url.ispath(abspath))
    assert(not url.ispath(exturl))
    assert(not url.ispath(nonpath))


def test_isabspath(relpath, abspath, exturl, nonpath):
    assert(not url.isabspath(relpath))
    assert(url.isabspath(abspath))
    assert(not url.isabspath(exturl))
    assert(not url.isabspath(exturl))


def test_issamehost(index, relpath, abspath, exturl, nonpath):
    assert(url.issamehost(index, relpath))
    assert(url.issamehost(index, abspath))
    assert(not url.issamehost(index, exturl))
    assert(url.issamehost(index, nonpath))


def test_issuburl(index, suburl, nonsuburl):
    assert(url.issuburl(index, suburl))
    assert(not url.issuburl(index, nonsuburl))


def test_fillurl(index, relpath, abspath):
    assert(
        url.fillurl(index, relpath) ==
        url.normalize(index + '/' + relpath)
    )
    parsedi = urlparse(index)
    parsedu = urlparse(abspath)
    assert(
        url.fillurl(index, abspath) ==
        url.normalize(
            '%s://%s/%s%s' % (
                parsedi.scheme, parsedi.hostname, parsedu.path.lstrip('/'),
                '?' + parsedu.query if parsedu.query else ''
            )
        )
    )


def test_normalize():
    assert(
        url.normalize('http://www.naver.com/a//b///c') ==
        'http://www.naver.com/a/b/c'
    )
    assert(
        url.normalize('http://www.naver.com///') ==
        'http://www.naver.com'
    )


def test_depth():
    assert(url.depth('http://www.naver.com/a/',
                     'http://www.naver.com/a/b/c') == 2)
    assert(url.depth('http://www.naver.com/a/',
                     'http://www.naver.com/a') == 0)
    assert(url.depth('http://www.naver.com/a/b',
                     'http://www.naver.com/a/b//c') == 1)
    assert(url.depth('http://www.naver.com/a/b/c', '/a/b/c/d/../d') == 1)
    assert(url.depth('http://www.naver.com/a/b', '/b/c/d/') == -1)
    assert(url.depth('http://www.naver.com/a/b', 'c/d') == 2)
