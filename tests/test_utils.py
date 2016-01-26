from urllib.parse import urlparse

import pytest
from news import utils


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
    assert(utils.ispath(relpath))
    assert(utils.ispath(abspath))
    assert(not utils.ispath(exturl))
    assert(not utils.ispath(nonpath))


def test_isabspath(relpath, abspath, exturl, nonpath):
    assert(not utils.isabspath(relpath))
    assert(utils.isabspath(abspath))
    assert(not utils.isabspath(exturl))
    assert(not utils.isabspath(exturl))


def test_issamehost(index, relpath, abspath, exturl, nonpath):
    assert(utils.issamehost(index, relpath))
    assert(utils.issamehost(index, abspath))
    assert(not utils.issamehost(index, exturl))
    assert(utils.issamehost(index, nonpath))


def test_issuburl(index, suburl, nonsuburl):
    assert(utils.issuburl(index, suburl))
    assert(not utils.issuburl(index, nonsuburl))


def test_fillurl(index, relpath, abspath):
    assert(utils.fillurl(index, relpath) ==
           utils.normalize(index + '/' + relpath))
    parsedi = urlparse(index)
    parsedu = urlparse(abspath)
    assert(
        utils.fillurl(index, abspath) ==
        utils.normalize(
            '%s://%s/%s%s' % (
                parsedi.scheme, parsedi.hostname, parsedu.path.lstrip('/'),
                '?' + parsedu.query if parsedu.query else '')
        )
    )


def test_normalize():
    assert(
        utils.normalize('http://www.naver.com/a//b///c') ==
        'http://www.naver.com/a/b/c'
    )
    assert(
        utils.normalize('http://www.naver.com///') ==
        'http://www.naver.com'
    )


def test_depth():
    assert(utils.depth('http://www.naver.com/a/',
                       'http://www.naver.com/a/b/c') == 2)
    assert(utils.depth('http://www.naver.com/a/',
                       'http://www.naver.com/a') == 0)
    assert(utils.depth('http://www.naver.com/a/b',
                       'http://www.naver.com/a/b//c') == 1)
    assert(utils.depth('http://www.naver.com/a/b/c', '/a/b/c/d/../d') == 1)
    assert(utils.depth('http://www.naver.com/a/b', '/b/c/d/') == -1)
    assert(utils.depth('http://www.naver.com/a/b', 'c/d') == 2)
