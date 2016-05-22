import pytest
from news.reporters import ReporterMeta
from news.reporters.url import URLReporter


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_worth_to_visit(django_backend, django_schedule, content_root):
    django_schedule.max_dist = 1
    django_schedule.max_depth = 1
    django_schedule.brothers = ['http://www.naver.com']
    django_schedule.save()

    meta = ReporterMeta(django_schedule)
    reporter = URLReporter(
        meta=meta, backend=django_backend,
        url=django_schedule.url
    )
    readable = reporter.parse(content_root)
    news = reporter.make_news(readable)

    assert(await reporter.worth_to_visit(news, django_schedule.url + '/1'))
    assert(not await reporter.worth_to_visit(news, django_schedule.url +
                                             '/1/2'))
    assert(await reporter.worth_to_visit(news, 'http://www.naver.com'))
    assert(await reporter.worth_to_visit(news, 'http://www.naver.com/123'))
    assert(not await reporter.worth_to_visit(news, django_schedule.url +
                                             '/badexperience'))


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_get_urls(django_backend, django_schedule):
    django_schedule.max_dist = 1
    django_schedule.max_depth = 1
    django_schedule.brothers = ['http://www.naver.com']
    django_schedule.save()

    meta = ReporterMeta(django_schedule)
    reporter = URLReporter(
        meta=meta, backend=django_backend,
        url=django_schedule.url,
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

    readable = reporter.parse(content)
    news = reporter.make_news(readable)
    worthy_urls = await reporter.get_urls(news)
    assert(django_schedule.url in worthy_urls)
    assert(django_schedule.url + '/' not in worthy_urls)
    assert(django_schedule.url + '/1' in worthy_urls)
    assert(django_schedule.url + '/1/2' not in worthy_urls)
    assert(django_schedule.url + '/badexperience' not in worthy_urls)
    assert('http://www.naver.com' in worthy_urls)
    assert('http://www.naver.com/' not in worthy_urls)
    assert('http://www.naver.com/123' in worthy_urls)


@pytest.mark.asyncio
async def test_report_visited(root_url_reporter):
    assert(root_url_reporter.url not in root_url_reporter._visited_urls)
    await root_url_reporter.report_visited()
    assert(root_url_reporter.url in root_url_reporter._visited_urls)


@pytest.mark.asyncio
async def test_already_visited(root_url_reporter):
    assert(not await root_url_reporter.already_visited(root_url_reporter.url))
    await root_url_reporter.report_visited()
    assert(await root_url_reporter.already_visited(root_url_reporter.url))


# ================
# Reporter callups
# ================

def test_inherit_meta(root_url_reporter, fetch_middleware):
    root_url_reporter.enhance_fetch(fetch_middleware)
    reporter = root_url_reporter.inherit_meta('/inherited')
    assert(reporter.meta == root_url_reporter.meta)
    assert(reporter.backend == root_url_reporter.backend)
    assert(reporter.predecessor == root_url_reporter)
    assert(reporter.fetch() == root_url_reporter.fetch() == 1)


@pytest.mark.django_db
def test_summon_reporter_for(root_url_reporter, django_news):
    reporter = root_url_reporter.summon_reporter_for(django_news)
    assert(reporter.url == django_news.url)
    assert(reporter.fetched_news == django_news)
    assert(reporter.predecessor == root_url_reporter)

    news = reporter.backend.News.create_instance(
        django_news.schedule, django_news.url + '/child', 'content',
        src=django_news
    )
    reporter.backend.save_news(news)
    successor_reporter = root_url_reporter.summon_reporter_for(news)
    assert(successor_reporter.url == news.url)
    assert(successor_reporter.fetched_news == news)
    assert(successor_reporter.predecessor == reporter)


@pytest.mark.django_db
def test_summon_reporters_for_intel(root_url_reporter, django_news):
    backend = root_url_reporter.backend
    create_instance = backend.News.create_instance

    news0 = create_instance(
        schedule=django_news.schedule,
        url=(django_news.url + '/child0'),
        content='content0',
        title='title0',
        summary='summary0',
        author='author0',
        parent=django_news
    )
    news1 = create_instance(
        schedule=django_news.schedule,
        url=(django_news.url + '/child1'),
        content='content1',
        author='author1',
        title='title1',
        parent=news0
    )
    news2 = create_instance(
        schedule=django_news.schedule,
        url=(django_news.url + '/child2'),
        content='content2',
        title='title2',
        summary='summary2',
        author='author2',
        parent=news1
    )
    news3 = create_instance(
        schedule=django_news.schedule,
        url=(django_news.url + '/child3'),
        content='content3',
        summary='summary3',
        title='title3',
        author='author3',
        src=news2
    )
    intel = [news0, news1, news2, news3]
    backend.save_news(*intel)

    root_url_reporter._intel = intel
    summoned = root_url_reporter.recruit_reporters()
    assert(summoned[0].url == news0.url)
    assert(summoned[1].url == news1.url)
    assert(summoned[2].url == news2.url)
    assert(summoned[3].url == news3.url)

    assert(summoned[0].fetched_news == news0)
    assert(summoned[1].fetched_news == news1)
    assert(summoned[2].fetched_news == news2)
    assert(summoned[3].fetched_news == news3)

    assert(summoned[0].root == root_url_reporter)
    assert(summoned[1].root == root_url_reporter)
    assert(summoned[2].root == root_url_reporter)
    assert(summoned[3].root == root_url_reporter)

    assert(summoned[0].parent.url == django_news.url)
    assert(summoned[0].parent.fetched_news == django_news)
    assert(summoned[1].parent == summoned[0])
    assert(summoned[2].parent == summoned[1])
    assert(summoned[3].parent == summoned[2])


def test_recruit_reporter_for(chief_reporter_fetched, url_child):
    reporter = chief_reporter_fetched.recruit_reporter_for(url_child)
    assert(reporter.url == url_child)
    assert(reporter.predecessor == chief_reporter_fetched)
    assert(reporter.backend == chief_reporter_fetched.backend)
