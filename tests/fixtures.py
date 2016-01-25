import json
import pytest

from news.site import Site
from news.news import News
from news.backends.json import JSONBackend
from news.backends.django import DjangoBackend


# =======
# Strings
# =======

@pytest.fixture
def url():
    return 'http://httpbin.org'


@pytest.fixture
def path(tmpdir):
    return tmpdir.mkdir('t').join('STORE.json')


@pytest.fixture
def valid_store_json(page):
    store = {
        'site': {1: page.site.to_json()},
        'page': {1: page.to_json()}
    }
    return json.dumps(store)


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
def json_backend(path):
    return JSONBackend(str(path))


@pytest.fixture
def django_backend():
    return DjangoBackend()


@pytest.fixture
def backend(json_backend):
    return json_backend


@pytest.fixture
def site(url):
    return Site(url)


@pytest.fixture
def page(site, url, content):
    return News(site, None, url, content)


@pytest.fixture
def text_page(site, url, text_content):
    return News(site, None, url, text_content)


@pytest.fixture
def local_link_page(site, url, local_link_content):
    return News(site, None, url, local_link_content)


@pytest.fixture
def external_link_page(site, url, external_link_content):
    return News(site, None, url, external_link_content)


@pytest.fixture
def hash_link_page(site, url, hash_link_content):
    return News(site, None, url, hash_link_content)
