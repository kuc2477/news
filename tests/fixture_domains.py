import pytest
from news.cover import Cover


@pytest.fixture
def cover(django_backend, django_schedule):
    return Cover.from_schedule(django_schedule, django_backend)
