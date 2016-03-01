import pytest
from news.cover import Cover


def test_cover_factory_method(django_backend, django_news, django_schedule):
    cover = Cover.from_schedule(django_schedule, django_backend)
    assert(cover.backend == django_backend)
    assert(cover.schedule == django_schedule)


@pytest.mark.asyncio
async def test_cover_prepare(cover, django_root_news, django_news):
    dispatch_middlewares = ['middlewares.dispatch_middleware']
    fetch_middlewares = ['middlewares.fetch_middleware']

    assert(cover.reporter is None)

    cover.prepare(report_experience='experiences.report_experience',
                  fetch_experience='experiences.fetch_experience',
                  dispatch_middlewares=dispatch_middlewares,
                  fetch_middlewares=fetch_middlewares)

    assert(cover.reporter is not None)
    assert(cover.reporter.backend == cover.backend)

    # check middlewares has been applied properly
    assert(cover.reporter.dispatch() == [1, 2, 3])
    assert(cover.reporter.fetch() == 1)

    # check experience has been configured properly
    assert(cover.reporter.worth_to_report(django_root_news))
    assert(cover.reporter.worth_to_visit(django_root_news, django_news.url))
