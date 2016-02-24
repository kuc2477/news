import pytest
from news.backends.django import DjangoBackend


@pytest.fixture
def django_backend(
        django_owner_class,
        django_schedule_class,
        django_news_class):
    return DjangoBackend(
        owner_class=django_owner_class,
        schedule_class=django_schedule_class,
        news_class=django_news_class
    )
