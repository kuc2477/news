import pytest
from news.backends.django import DjangoBackend
from news.backends.sqlalchemy import SQLAlchemyBackend


@pytest.fixture
def django_backend(
        django_owner_model,
        django_schedule_model,
        django_news_model):
    return DjangoBackend.create_backend(
        owner_class=django_owner_model,
        schedule_class=django_schedule_model,
        news_class=django_news_model
    )


@pytest.fixture
def sa_backend(sa_owner_model, sa_schedule_model,
               sa_news_model, sa_session):
    backend = SQLAlchemyBackend.create_backend(
        bind=sa_session,
        owner_class=sa_owner_model,
        schedule_class=sa_schedule_model,
        news_class=sa_news_model
    )
    return backend
