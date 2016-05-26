import functools
import pytest
from news.reporters.url import URLReporter
from news.contrib.logging.middlewares import (
    logging_dispatch_middleware,
    logging_fetch_middleware,
)


@pytest.mark.asyncio
async def test_cover_prepare(cover, django_root_news):
    # dispatch middleware
    def dispatch_middleware(reporter, dispatch):
        @functools.wraps(dispatch)
        async def enhanced():
            print('hello dispatch')
            return [1, 2, 3]
        return enhanced

    # fetch middleware
    def fetch_middleware(reporter, fetch):
        @functools.wraps(fetch)
        async def enhanced():
            print('hello fetch')
            return 10
        return enhanced

    assert(cover.reporter is None)
    cover.prepare(
        reporter_class=URLReporter,
        dispatch_middlewares=[
            logging_fetch_middleware,
            dispatch_middleware
        ],
        fetch_middlewares=[
            logging_dispatch_middleware,
            fetch_middleware
        ]
    )

    assert(cover.reporter is not None)
    assert(cover.reporter.backend == cover.backend)

    # check middlewares has been applied properly
    assert(await cover.reporter.dispatch() == [1, 2, 3])
    assert(await cover.reporter.fetch() == 10)
