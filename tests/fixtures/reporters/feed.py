import pytest
from news.reporters import ReporterMeta
from news.reporters.feed import AtomReporter, RSSReporter


@pytest.fixture
def rss_reporter(sa_schedule, sa_backend):
    meta = ReporterMeta(schedule=sa_schedule)
    return RSSReporter(meta=meta, backend=sa_backend)


@pytest.fixture
def atom_reporter(sa_schedule, sa_backend):
    meta = ReporterMeta(schedule=sa_schedule)
    return AtomReporter(meta=meta, backend=sa_backend)
