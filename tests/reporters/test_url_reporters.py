import pytest
from news.reporters import ReporterMeta
from news.reporters.url import URLReporter


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
    assert(django_schedule.url + '/1/2' in worthy_urls)
    assert('http://www.naver.com' in worthy_urls)
    assert('http://www.naver.com/' not in worthy_urls)
    assert('http://www.naver.com/123' in worthy_urls)


@pytest.mark.asyncio
async def test_report_visited(django_root_url_reporter):
    assert(django_root_url_reporter.url not in
           django_root_url_reporter._visited_urls)
    await django_root_url_reporter.report_visit()
    assert(django_root_url_reporter.url in
           django_root_url_reporter._visited_urls)


@pytest.mark.asyncio
async def test_already_visited(django_root_url_reporter):
    assert(not await django_root_url_reporter.already_visited(
        django_root_url_reporter.url
    ))
    await django_root_url_reporter.report_visit()
    assert(await django_root_url_reporter.already_visited(
        django_root_url_reporter.url
    ))


@pytest.mark.django_db
def test_batch_traversing_reporter_mixin(
        django_root_url_reporter, django_child_news):
    backend = django_root_url_reporter.backend
    create_instance = backend.News.create_instance

    news0 = create_instance(
        schedule=django_child_news.schedule,
        url=(django_child_news.url + '/child0'),
        content='content0',
        title='title0',
        summary='summary0',
        author='author0',
        parent=django_child_news
    )
    news1 = create_instance(
        schedule=django_child_news.schedule,
        url=(django_child_news.url + '/child1'),
        content='content1',
        author='author1',
        title='title1',
        parent=news0,
        summary='summary1',
    )
    news2 = create_instance(
        schedule=django_child_news.schedule,
        url=(django_child_news.url + '/child2'),
        content='content2',
        title='title2',
        summary='summary2',
        author='author2',
        parent=news1
    )
    news3 = create_instance(
        schedule=django_child_news.schedule,
        url=(django_child_news.url + '/child3'),
        content='content3',
        summary='summary3',
        title='title3',
        author='author3',
        parent=news2
    )
    intel = [news0, news1, news2, news3]
    backend.save_news(*intel)

    django_root_url_reporter._intel = intel
    summoned = django_root_url_reporter.recruit_reporters()
    assert(summoned[0].url == news0.url)
    assert(summoned[1].url == news1.url)
    assert(summoned[2].url == news2.url)
    assert(summoned[3].url == news3.url)

    assert(summoned[0].fetched_news == news0)
    assert(summoned[1].fetched_news == news1)
    assert(summoned[2].fetched_news == news2)
    assert(summoned[3].fetched_news == news3)

    assert(summoned[0].root == django_root_url_reporter)
    assert(summoned[1].root == django_root_url_reporter)
    assert(summoned[2].root == django_root_url_reporter)
    assert(summoned[3].root == django_root_url_reporter)

    assert(summoned[0].parent.url == django_child_news.url)
    assert(summoned[0].parent.fetched_news == django_child_news)
    assert(summoned[1].parent == summoned[0])
    assert(summoned[2].parent == summoned[1])
    assert(summoned[3].parent == summoned[2])
