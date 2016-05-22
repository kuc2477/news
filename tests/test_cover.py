import functools
import pytest
from news.reporters.url import URLReporter


@pytest.mark.asyncio
async def test_cover_prepare(cover, django_root_news, django_news):
    # dispatch middleware
    def dispatch_middleware(reporter, dispatch):
        @functools.wraps(dispatch)
        def enhanced(r):
            return [1, 2, 3]
        return enhanced

    # fetch middleware
    def fetch_middleware(reporter, fetch):
        @functools.wraps(fetch)
        def enhanced(r):
            return 10
        return enhanced

    assert(cover.reporter is None)
    cover.prepare(reporter_class=URLReporter,
                  dispatch_middlewares=[dispatch_middleware],
                  fetch_middlewares=[fetch_middleware])

    assert(cover.reporter is not None)
    assert(cover.reporter.backend == cover.backend)

    # check middlewares has been applied properly
    assert(cover.reporter.dispatch() == [1, 2, 3])
    assert(cover.reporter.fetch() == 10)
