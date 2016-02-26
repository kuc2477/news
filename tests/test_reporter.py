from news.models.abstract import AbstractSchedule


def test_reporter_meta_attr_types(reporter_meta):
    assert(isinstance(reporter_meta.schedule, AbstractSchedule))
    assert(isinstance(reporter_meta.intel, list))
    assert(callable(reporter_meta.report_experience))
    assert(callable(reporter_meta.fetch_experience))
    assert(isinstance(reporter_meta.dispatch_middlewares, list))
    assert(isinstance(reporter_meta.fetch_middlewares, list))


def test_chief_reporter_attrs(chief_reporter):
    assert(chief_reporter.predecessor is None)
    assert(chief_reporter.fetched_news is None)
    assert(chief_reporter.schedule == chief_reporter.meta.schedule)
    assert(chief_reporter.owner == chief_reporter.meta.owner)
    assert(chief_reporter.filter_options == chief_reporter.meta.filter_options)


def test_chief_reporter_fetched_attrs(chief_reporter):
    pass


def test_successor_reporter_attrs(successor_reporter):
    pass


def test_successor_reporter_fetched_attrs(successor_reporter):
    pass


def test_make_news(chief_reporter, content_root):
    pass


def test_enhance_dispatch(chief_reporter):
    pass


def test_enhance_fetch(chief_reporter):
    pass
