import pytest


@pytest.fixture
def url():
    return 'http://httpbin.org'


@pytest.fixture(params=[
    'text only response',
    '<a href="/path/to/other/news">response with local link</a>',
    '<a href="http://www.naver.com/path/">response with local link</a>',
    '<a href="http://www.daum.net">response with external link</a>',
    '<a href="#hash">response with only hash</a>',
])
def content(request):
    return request.param


@pytest.fixture
def text_content():
    return 'text only response'


@pytest.fixture(params=[
    '<a href="/path/to/other/news">response with local link</a>',
    '<a href="http://httpbin.org">response with local link</a>',
])
def local_link_content(request):
    return request.param


@pytest.fixture
def external_link_content():
    return '<a href="http://www.daum.net">response with external link</a>'


@pytest.fixture
def hash_link_content():
    return '<a href="#hash">response with only hash</a>'
