import pytest
from news.backends.sqlalchemy import SQLAlchemyBackend


@pytest.fixture
def sa_backend(sa_owner_model, sa_schedule_model,
               sa_news_model, sa_session):
    backend = SQLAlchemyBackend.create_backend(
        bind=sa_session,
        owner_model=sa_owner_model,
        schedule_model=sa_schedule_model,
        news_model=sa_news_model
    )
    return backend
