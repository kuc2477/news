from news.reporters import ReporterMeta


def test_enhance_dispatch(mocker, chief_reporter):
    mocker.patch.object(chief_reporter, 'dispatch', return_value=[4, 5, 6])

    assert(chief_reporter.dispatch() == [4, 5, 6])
    chief_reporter.enhance_dispatch('middlewares.dispatch_middleware')
    assert(chief_reporter.dispatch() == [1, 2, 3])


def test_enhance_fetch(mocker, chief_reporter):
    mocker.patch.object(chief_reporter, 'fetch', return_value=0)

    assert(chief_reporter.fetch() == 0)
    chief_reporter.enhance_fetch('middlewares.fetch_middleware')
    assert(chief_reporter.fetch() == 1)


def test_report_news(chief_reporter, content_root):
    news = chief_reporter.make_news(content_root)
    assert(not chief_reporter.backend.news_exists_by(news.owner, news.url))
    chief_reporter.report_news(news)
    assert(chief_reporter.backend.news_exists_by(news.owner, news.url))
