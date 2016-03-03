import pytest
from news.backends.django import DjangoBackend
from news.backends.sqlalchemy import SQLAlchemyBackend


@pytest.fixture
def django_backend(
        django_owner_class,
        django_schedule_class,
        django_news_class):
    return DjangoBackend.create_backend(
        owner_class=django_owner_class,
        schedule_class=django_schedule_class,
        news_class=django_news_class
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
