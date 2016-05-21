import pytest
from news.reporters import ReporterMeta
from news.reporters.url import URLReporter


@pytest.fixture
def root_url_reporter(sa_schedule, sa_backend):
    meta = ReporterMeta(schedule=sa_schedule)
    return URLReporter(meta=meta, backend=sa_backend)


@pytest.fixture
def child_url_reporter(root_url_reporter, sa_schedule, sa_backend, url_child):
    meta = ReporterMeta(schedule=sa_schedule)
    return URLReporter(meta=meta, backend=sa_backend, parent=root_url_reporter)
