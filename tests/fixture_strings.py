import pytest


@pytest.fixture
def url():
    return 'http://httpbin.org'


# ============
# Root & child
# ============

@pytest.fixture
def url_root():
    return 'http://httpbin.org'


@pytest.fixture
def url_child():
    return 'http://httpbin.org/html'


@pytest.fixture
def content_root():
    return ("""
<html>
    <head></head>
    <body>
        <h1>Herman Melville - Moby-Dick</h1>
        <div>
            <p>
                Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
                sed diam nonumy eirmod tempor invidunt ut labore et dolore
                magna aliquyam erat, sed diam voluptua. At vero eos et accusam
                et justo duo dolores et ea rebum. Stet clita kasd gubergren,
                no sea takimata sanctus est Lorem ipsum dolor sit amet.
            </p>
            <a href='/html'>link</a>
        </div>
    </body>
</html>
""")


@pytest.fixture
def content_child():
    return ("""
<html>
    <head></head>
    <body>
        <h1>Herman Melville - Moby-Dick</h1>
        <div>
            <p>
                Lorem ipsum dolor sit amet, consetetur sadipscing elitr,
                sed diam nonumy eirmod tempor invidunt ut labore et dolore
                magna aliquyam erat, sed diam voluptua. At vero eos et accusam
                et justo duo dolores et ea rebum. Stet clita kasd gubergren,
                no sea takimata sanctus est Lorem ipsum dolor sit amet.
            </p>
        </div>
    </body>
</html>
""")


# ========
# Contents
# ========

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
