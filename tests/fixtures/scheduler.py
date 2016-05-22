import pytest
from news.scheduler import Scheduler


@pytest.fixture
def sa_scheduler(sa_backend, persister, celery):
    return Scheduler(backend=sa_backend, celery=celery, persister=persister)


@pytest.fixture
def django_scheduler(django_backend, persister, celery):
    return Scheduler(backend=django_backend, celery=celery,
                     persister=persister)
