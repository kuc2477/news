import pytest
from news.reporters import ReporterMeta
from news.reporters.url import URLReporter


@pytest.fixture
def sa_root_url_reporter(sa_schedule, sa_backend):
    meta = ReporterMeta(schedule=sa_schedule)
    return URLReporter(meta=meta, backend=sa_backend)


@pytest.fixture
def sa_child_url_reporter(sa_root_url_reporter, sa_schedule, 
                          sa_backend, url_child):
    meta = ReporterMeta(schedule=sa_schedule)
    return URLReporter(meta=meta, backend=sa_backend, 
                       parent=sa_root_url_reporter)


@pytest.fixture
def django_root_url_reporter(django_schedule, django_backend):
    meta = ReporterMeta(schedule=django_schedule)
    return URLReporter(meta=meta, backend=django_backend)


@pytest.fixture
def django_child_url_reporter(django_root_url_reporter, django_schedule,
                              django_backend, url_child):
    meta = ReporterMeta(schedule=django_schedule)
    return URLReporter(meta=meta, backend=django_backend, 
                       parent=django_root_url_reporter)
