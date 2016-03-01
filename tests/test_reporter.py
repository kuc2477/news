from functools import wraps
import pytest
from news.models.abstract import AbstractSchedule
from news.reporter import Reporter, ReporterMeta


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


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_worth_to_visit(django_backend, django_schedule, content_root):
    django_schedule.max_dist = 1
    django_schedule.max_depth = 1
    django_schedule.brothers = ['http://www.naver.com']
    django_schedule.save()

    def fetch_experience(schedule, news, url):
        return 'badexperience' not in url

    reporter_meta = ReporterMeta(
        django_schedule, fetch_experience=fetch_experience
    )
    reporter = Reporter(
        django_schedule.url, reporter_meta, django_backend
    )
    news = reporter.make_news(content_root)

    assert(await reporter.worth_to_visit(news, django_schedule.url + '/1'))
    assert(not await reporter.worth_to_visit(news, django_schedule.url +
                                             '/1/2'))
    assert(await reporter.worth_to_visit(news, 'http://www.naver.com'))
    assert(await reporter.worth_to_visit(news, 'http://www.naver.com/123'))
    assert(not await reporter.worth_to_visit(news, django_schedule.url +
                                             '/badexperience'))


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_get_worthy_urls(django_backend, django_schedule):
    django_schedule.max_dist = 1
    django_schedule.max_depth = 1
    django_schedule.brothers = ['http://www.naver.com']
    django_schedule.save()

    def fetch_experience(schedule, news, url):
        return 'badexperience' not in url

    reporter_meta = ReporterMeta(
        django_schedule, fetch_experience=fetch_experience
    )
    reporter = Reporter(
        django_schedule.url, reporter_meta, django_backend
    )
    content = (
        '''
        <a href="{}" />
        <a href="{}" />
        <a href="{}" />
        <a href="{}" />
        <a href="{}" />
        <a href="{}" />
        <a href="{}" />
        <a href="{}" />
        '''.format(
            django_schedule.url,
            django_schedule.url + '/',
            django_schedule.url + '/1',
            django_schedule.url + '/1/2',
            django_schedule.url + '/badexperience',
            'http://www.naver.com',
            'http://www.naver.com/',
            'http://www.naver.com/123',
        )
    )

    news = reporter.make_news(content)
    worthy_urls = await reporter.get_worthy_urls(news)
    assert(django_schedule.url in worthy_urls)
    assert(django_schedule.url + '/' not in worthy_urls)
    assert(django_schedule.url + '/1' in worthy_urls)
    assert(django_schedule.url + '/1/2' not in worthy_urls)
    assert(django_schedule.url + '/badexperience' not in worthy_urls)
    assert('http://www.naver.com' in worthy_urls)
    assert('http://www.naver.com/' not in worthy_urls)
    assert('http://www.naver.com/123' in worthy_urls)


def test_worth_to_report(django_backend, django_schedule):
    reporter_meta = ReporterMeta(
        django_schedule,
        report_experience=(
            lambda s, n:
            'valuable' in n.content and 'not' not in n.content
        )
    )
    reporter = Reporter(
        django_schedule.url,
        reporter_meta,
        django_backend,
    )

    valuable_news = reporter.make_news('valuable')
    useless_news = reporter.make_news('not valuable')
    assert(reporter.worth_to_report(valuable_news))
    assert(not reporter.worth_to_report(useless_news))


# ================
# Reporter callups
# ================

def test_inherit_meta(chief_reporter, fetch_middleware):
    chief_reporter.enhance_fetch(fetch_middleware)
    reporter = chief_reporter.inherit_meta('/inherited')
    assert(reporter.meta == chief_reporter.meta)
    assert(reporter.backend == chief_reporter.backend)
    assert(reporter.predecessor == chief_reporter)
    assert(reporter.fetch() == chief_reporter.fetch() == 1)


@pytest.mark.django_db
def test_summon_reporter_for(chief_reporter, django_news):
    reporter = chief_reporter.summon_reporter_for(django_news)
    assert(reporter.url == django_news.url)
    assert(reporter.fetched_news == django_news)
    assert(reporter.predecessor == chief_reporter)

    news = reporter.backend.news_class.create_instance(
        django_news.schedule, django_news.url + '/child', 'content',
        src=django_news
    )
    reporter.backend.save_news(news)
    successor_reporter = chief_reporter.summon_reporter_for(news)
    assert(successor_reporter.url == news.url)
    assert(successor_reporter.fetched_news == news)
    assert(successor_reporter.predecessor == reporter)


@pytest.mark.django_db
def test_summon_reporters_for_intel(chief_reporter, django_news):
    backend = chief_reporter.backend
    create_instance = backend.news_class.create_instance

    news0 = create_instance(
        django_news.schedule, django_news.url + '/child0', 'content0',
        src=django_news
    )
    news1 = create_instance(
        django_news.schedule, django_news.url + '/child1', 'content1',
        src=news0
    )
    news2 = create_instance(
        django_news.schedule, django_news.url + '/child2', 'content2',
        src=news1
    )
    news3 = create_instance(
        django_news.schedule, django_news.url + '/child3', 'content3',
        src=news2
    )
    intel = [news0, news1, news2, news3]
    backend.save_news(*intel)

    summoned = chief_reporter.summon_reporters_for_intel(intel)
    assert(summoned[0].url == news0.url)
    assert(summoned[1].url == news1.url)
    assert(summoned[2].url == news2.url)
    assert(summoned[3].url == news3.url)

    assert(summoned[0].fetched_news == news0)
    assert(summoned[1].fetched_news == news1)
    assert(summoned[2].fetched_news == news2)
    assert(summoned[3].fetched_news == news3)

    assert(summoned[0].chief == chief_reporter)
    assert(summoned[1].chief == chief_reporter)
    assert(summoned[2].chief == chief_reporter)
    assert(summoned[3].chief == chief_reporter)

    assert(summoned[0].predecessor.url == django_news.url)
    assert(summoned[0].predecessor.fetched_news == django_news)
    assert(summoned[1].predecessor == summoned[0])
    assert(summoned[2].predecessor == summoned[1])
    assert(summoned[3].predecessor == summoned[2])


def test_recruit_reporter_for(chief_reporter_fetched, url_child):
    reporter = chief_reporter_fetched.recruit_reporter_for(url_child)
    assert(reporter.url == url_child)
    assert(reporter.predecessor == chief_reporter_fetched)
    assert(reporter.backend == chief_reporter_fetched.backend)
