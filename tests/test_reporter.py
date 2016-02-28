from functools import wraps
import pytest
from news.models.abstract import AbstractSchedule


# ===============
# Attribute tests
# ===============

def test_reporter_meta_attrs(reporter_meta):
    assert(isinstance(reporter_meta.schedule, AbstractSchedule))
    assert(isinstance(reporter_meta.intel, list))
    assert(callable(reporter_meta.report_experience))
    assert(callable(reporter_meta.fetch_experience))


def test_chief_reporter_attrs(chief_reporter):
    assert(chief_reporter.predecessor is None)
    assert(chief_reporter.fetched_news is None)
    assert(chief_reporter.schedule == chief_reporter.meta.schedule)
    assert(chief_reporter.owner == chief_reporter.meta.owner)
    assert(chief_reporter.filter_options == chief_reporter.meta.filter_options)


def test_chief_reporter_fetched_attrs(chief_reporter_fetched):
    assert(chief_reporter_fetched.predecessor is None)
    assert(chief_reporter_fetched.fetched_news is not None)
    assert(chief_reporter_fetched.schedule ==
           chief_reporter_fetched.meta.schedule)
    assert(chief_reporter_fetched.owner ==
           chief_reporter_fetched.meta.owner)
    assert(chief_reporter_fetched.filter_options ==
           chief_reporter_fetched.meta.filter_options)


def test_successor_reporter_attrs(chief_reporter_fetched,
                                  successor_reporter):
    assert(successor_reporter.predecessor == chief_reporter_fetched)
    assert(successor_reporter.fetched_news is None)
    assert(successor_reporter.schedule ==
           successor_reporter.meta.schedule)
    assert(successor_reporter.owner ==
           successor_reporter.meta.owner)
    assert(successor_reporter.filter_options ==
           successor_reporter.meta.filter_options)


def test_successor_reporter_fetched_attrs(chief_reporter_fetched,
                                          successor_reporter_fetched):
    assert(successor_reporter_fetched.predecessor == chief_reporter_fetched)
    assert(successor_reporter_fetched.fetched_news is not None)
    assert(successor_reporter_fetched.schedule ==
           successor_reporter_fetched.meta.schedule)
    assert(successor_reporter_fetched.owner ==
           successor_reporter_fetched.meta.owner)
    assert(successor_reporter_fetched.filter_options ==
           successor_reporter_fetched.meta.filter_options)


# ==================
# News / Middlewares
# ==================

def test_make_news(chief_reporter, content_root):
    news = chief_reporter.make_news(content_root)
    assert(isinstance(news, chief_reporter.backend.news_class))
    assert(news.url == chief_reporter.url)
    assert(news.content == content_root)
    assert(news.schedule == chief_reporter.schedule)
    assert(news.src is None)


def test_enhance_dispatch(mocker, chief_reporter):
    mocker.patch.object(chief_reporter, 'dispatch', return_value=[1, 2, 3])

    def middleware(reporter, dispatch):
        @wraps(dispatch)
        def enhanced(bulk_report=False):
            total = dispatch(bulk_report)
            total += [4, 5, 6]
            return total
        return enhanced

    assert(chief_reporter.dispatch() == [1, 2, 3])
    chief_reporter.enhance_dispatch(middleware)
    assert(chief_reporter.dispatch() == [1, 2, 3, 4, 5, 6])


def test_enhance_fetch(mocker, chief_reporter):
    mocker.patch.object(chief_reporter, 'fetch', return_value=0)

    def middleware(reporter, fetch):
        @wraps(fetch)
        def enhanced(immediate_report=True):
            fetched = fetch(immediate_report)
            return None if fetched == 0 else fetched
        return enhanced

    assert(chief_reporter.fetch() == 0)
    chief_reporter.enhance_fetch(middleware)
    assert(chief_reporter.fetch() is None)


# ===================
# Reporter operations
# ===================

def test_report_news(chief_reporter, content_root):
    news = chief_reporter.make_news(content_root)
    assert(not chief_reporter.backend.news_exists(news.owner, news.url))
    chief_reporter.report_news(news)
    assert(chief_reporter.backend.news_exists(news.owner, news.url))


@pytest.mark.asyncio
async def test_report_visited(chief_reporter, content_root):
    assert(chief_reporter.url not in chief_reporter._visited_urls)
    await chief_reporter.report_visited()
    assert(chief_reporter.url in chief_reporter._visited_urls)


@pytest.mark.asyncio
async def test_already_visited(chief_reporter):
    assert(not await chief_reporter.already_visited(chief_reporter.url))
    await chief_reporter.report_visited()
    assert(await chief_reporter.already_visited(chief_reporter.url))


@pytest.mark.asyncio
async def test_get_worthy_urls():
    pass


@pytest.mark.asyncio
async def test_worth_to_visit():
    pass


def test_worth_to_report():
    pass


# ================
# Reporter callups
# ================

def test_take_responsibility():
    pass


def test_summon_reporter_for():
    pass


def test_summon_reporters_for_intel():
    pass


def test_recruit_reporter_for():
    pass


def test_recruit_reporters_for_urls():
    pass


def test_call_up_reporters():
    pass
