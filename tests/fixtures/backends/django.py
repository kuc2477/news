import pytest
from news.backends.django import DjangoBackend


@pytest.fixture
def django_backend(
        django_owner_model,
        django_schedule_model,
        django_news_model):
    return DjangoBackend.create_backend(
        owner_model=django_owner_model,
        schedule_model=django_schedule_model,
        news_model=django_news_model
    )
