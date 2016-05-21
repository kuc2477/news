import pytest
from news.cover import Cover


@pytest.fixture
def cover(django_backend, django_schedule):
    return Cover(schedule=django_schedule, backend=django_backend)
