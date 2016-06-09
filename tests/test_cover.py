import pytest
from news.reporters.url import URLReporter
from news.contrib.logging.middlewares import (
    request_log_middleware,
    response_log_middleware,
    report_log_middleware,
)


@pytest.mark.asyncio
async def test_cover_prepare(cover, django_root_news):
    assert(cover.reporter is None)
    cover.prepare(
        reporter_class=URLReporter,
        request_middlewares=[request_log_middleware],
        response_middlewares=[response_log_middleware],
        report_middlewares=[report_log_middleware],
    )

    assert(cover.reporter is not None)
    assert(cover.reporter.backend == cover.backend)
    assert(cover.request_middlewares)
    assert(cover.response_middlewares)
    assert(cover.report_middlewares)
