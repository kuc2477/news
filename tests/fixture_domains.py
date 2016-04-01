import pytest
from celery import Celery
from redis import Redis
from news.cover import Cover
from news.reporter import ReporterMeta, Reporter
from news.scheduler import Scheduler
from news.persister import SchedulePersister


@pytest.fixture
def cover(django_backend, django_schedule):
    return Cover.from_schedule(django_schedule, django_backend)


@pytest.fixture
def reporter_meta(django_schedule):
    return ReporterMeta(django_schedule)


@pytest.fixture
def dispatch_middleware():
    return 'middlewares.dispatch_middleware'


@pytest.fixture
def fetch_middleware():
    return 'middlewares.fetch_middleware'


@pytest.fixture
def chief_reporter(url_root, reporter_meta, django_backend):
    return Reporter(url_root,  reporter_meta, django_backend)


@pytest.fixture
def chief_reporter_fetched(chief_reporter, content_root):
    reporter = chief_reporter
    reporter.report_visited()
    reporter.fetched_news = reporter.make_news(content_root)
    return reporter


@pytest.fixture
def successor_reporter(url_child, reporter_meta, django_backend,
                       chief_reporter_fetched):
    return Reporter(url_child, reporter_meta, django_backend,
                    predecessor=chief_reporter_fetched)


@pytest.fixture
def successor_reporter_fetched(successor_reporter, content_child):
    reporter = successor_reporter
    reporter.report_visited()
    reporter.fetched_news = reporter.make_news(content_child)
    return reporter


@pytest.fixture(scope='session')
def persister():
    return SchedulePersister(Redis())


@pytest.fixture
def scheduler(django_backend):
    return Scheduler(
        django_backend, Celery(),
        report_experience='experiences.report_experience',
        fetch_experience='experiences.fetch_experience',
        dispatch_middlewares=['middlewares.dispatch_middleware'],
        fetch_middlewares=['middlewares.fetch_middleware']
    )


@pytest.fixture
def sa_scheduler(sa_backend):
    return Scheduler(
        sa_backend, Celery(),
        report_experience='experiences.report_experience',
        fetch_experience='experiences.fetch_experience',
        dispatch_middlewares=['middlewares.dispatch_middleware'],
        fetch_middlewares=['middlewares.fetch_middleware']
    )
