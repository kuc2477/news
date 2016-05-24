import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer
)
from news.models import sqlalchemy as sa


TEST_DB = 'test.db'
TEST_DB_PATH = ':memory:'
TEST_DB_URI = 'sqlite:///' + TEST_DB_PATH


# ============================
# SQLAlchemy engine / sessions
# ============================

@pytest.fixture(scope='session')
def sa_engine():
    return create_engine(TEST_DB_URI)


@pytest.fixture(scope='session')
def sa_declarative_base():
    return declarative_base()


@pytest.fixture(scope='session')
def sa_db(request,
          sa_declarative_base, sa_engine,
          sa_owner_model, sa_schedule_model, sa_news_model):
    # create tables
    sa_declarative_base.metadata.create_all(bind=sa_engine)

    # clear tables
    def teardown():
        sa_declarative_base.metadata.drop_all(bind=sa_engine)

    request.addfinalizer(teardown)


@pytest.fixture(scope='function')
def sa_session(request, sa_db, sa_engine):
    connection = sa_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    # rollback test transaction, close connection and remove session
    def teardown():
        session.close()
        transaction.rollback()
        connection.close()

    request.addfinalizer(teardown)

    return session


# =================
# SQLAlchemy Models
# =================

@pytest.fixture(scope='session')
def sa_abc_schedule(sa_owner_model):
    return sa.create_abc_schedule(sa_owner_model)


@pytest.fixture(scope='session')
def sa_abc_news(sa_schedule_model):
    return sa.create_abc_news(sa_schedule_model)


@pytest.fixture(scope='session')
def sa_owner_model(sa_declarative_base):

    class User(sa_declarative_base):
        __tablename__ = 'user'
        id = Column(Integer, primary_key=True)

    return User


@pytest.fixture(scope='session')
def sa_schedule_model(sa_abc_schedule, sa_declarative_base, persister):
    return sa.create_schedule(sa_abc_schedule, sa_declarative_base,
                              persister=persister)


@pytest.fixture(scope='session')
def sa_news_model(sa_abc_news, sa_declarative_base):
    return sa.create_news(sa_abc_news, sa_declarative_base)


# ===========================
# SQLAlchemy model instances
# ===========================

@pytest.fixture
def sa_owner(request, sa_session, sa_owner_model):
    owner = sa_owner_model()
    sa_session.add(owner)
    sa_session.commit()

    def teardown():
        sa_session.delete(owner)
        sa_session.commit()
    request.addfinalizer(teardown)

    return owner


@pytest.fixture
def sa_schedule(request, sa_session, sa_owner, sa_schedule_model, url_root):
    schedule = sa_schedule_model(owner=sa_owner, url=url_root)
    sa_session.add(schedule)
    sa_session.commit()

    def teardown():
        sa_session.delete(schedule)
        sa_session.commit()
    request.addfinalizer(teardown)

    return schedule


@pytest.fixture
def sa_root_news(request, sa_session, sa_schedule, sa_news_model,
                 url_root, title_root, author_root, content_root,
                 summary_root):
    news = sa_news_model(
        schedule=sa_schedule,
        url=url_root,
        title=title_root,
        author=author_root,
        content=content_root,
        summary=summary_root
    )
    sa_session.add(news)
    sa_session.commit()

    def teardown():
        sa_session.delete(news)
        sa_session.commit()
    request.addfinalizer(teardown)

    return news


@pytest.fixture
def sa_child_news(request, sa_session, sa_schedule, sa_root_news,
                  sa_news_model, url_child, author_child,
                  title_child, content_child, summary_child):
    news = sa_news_model(
        schedule=sa_schedule, parent=sa_root_news,
        url=url_child, author=author_child, content=content_child,
        title=title_child, summary=summary_child
    )
    sa_session.add(news)
    sa_session.commit()

    def teardown():
        sa_session.delete(news)
        sa_session.commit()
    request.addfinalizer(teardown)

    return news
