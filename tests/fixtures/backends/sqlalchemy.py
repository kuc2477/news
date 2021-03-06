import pytest
from news.backends.sqlalchemy import SQLAlchemyBackend


@pytest.fixture
def sa_backend(sa_schedule_model, sa_news_model, sa_session):
    backend = SQLAlchemyBackend.create_backend(
        schedule_model=sa_schedule_model,
        news_model=sa_news_model
    ).bind(sa_session)
    return backend
