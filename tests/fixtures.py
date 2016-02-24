import pytest
from news.backends.django import DjangoBackend


# =======
# Strings
# =======

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


# ======
# Models
# ======

@pytest.fixture
def django_backend():
    return DjangoBackend()


@pytest.fixture
def owner():
    pass


@pytest.fixture
def schedule_meta():
    pass


@pytest.fixture
def news(url, content):
    return News(url, content)


@pytest.fixture
def news_with_text_only(site, url, text_content):
    return News(site, None, url, text_content)


@pytest.fixture
def news_with_local_link(site, url, local_link_content):
    return News(site, None, url, local_link_content)


@pytest.fixture
def news_with_external_link(site, url, external_link_content):
    return News(site, None, url, external_link_content)


@pytest.fixture
def news_with_hash_link(site, url, hash_link_content):
    return News(site, None, url, hash_link_content)
