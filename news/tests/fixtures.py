import pytest

from ..site import Site
from ..page import Page
from ..backends.json import JSONBackend


# =======
# Strings
# =======

@pytest.fixture
def url():
    return 'http://httpbin.org'

@pytest.fixture(params=[
    'text only response',
    '<a href="/path/to/other/page">response with local link</a>',
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
    '<a href="/path/to/other/page">response with local link</a>',
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


# ====================
# News related objects
# ====================

@pytest.fixture
def ranker():
    return None

@pytest.fixture
def path(tmpdir):
    return tmpdir.mkdir('t').join('STORE.json')

@pytest.fixture
def backend(path):
    return JSONBackend(str(path))

@pytest.fixture
def site(url, backend, ranker):
    return Site(url, backend, ranker)

@pytest.fixture
def page(site, url, content):
    return Page(site, url, content, None)

@pytest.fixture
def text_page(site, url, text_content):
    return Page(site, url, text_content, None)

@pytest.fixture
def local_link_page(site, url, local_link_content):
    return Page(site, url, local_link_content, None)

@pytest.fixture
def external_link_page(site, url, external_link_content):
    return Page(site, url, external_link_content, None)

@pytest.fixture
def hash_link_page(site, url, hash_link_content):
    return Page(site, url, hash_link_content, None)
