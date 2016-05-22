import functools


def test_enhance_dispatch(mocker, root_url_reporter):
    def middleware(reporter, dispatch):
        @functools.wraps(dispatch)
        def enhanced():
            news_list = dispatch()
            return [1, 2, 3] + news_list
        return enhanced

    mocker.patch.object(root_url_reporter, 'dispatch', return_value=[4, 5, 6])
    assert(root_url_reporter.dispatch() == [4, 5, 6])
    root_url_reporter.enhance_dispatch(middleware)
    assert(root_url_reporter.dispatch() == [1, 2, 3, 4, 5, 6])


def test_enhance_fetch(mocker, root_url_reporter):
    def middleware(reporter, fetch):
        @functools.wraps(fetch)
        def enhanced():
            return 1
        return enhanced

    mocker.patch.object(root_url_reporter, 'fetch', return_value=0)
    assert(root_url_reporter.fetch() == 0)
    root_url_reporter.enhance_fetch(middleware)
    assert(root_url_reporter.fetch() == 1)


def test_report_news(root_url_reporter, content_root):
    readable = root_url_reporter.parse(content_root)
    news = root_url_reporter.make_news(readable)
    assert(not root_url_reporter.backend.news_exists_by(news.owner, news.url))
    root_url_reporter.report_news(news)
    assert(root_url_reporter.backend.news_exists_by(news.owner, news.url))
