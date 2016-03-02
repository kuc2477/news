import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


TEST_DB = 'test.db'
TEST_DB_PATH = ''
TEST_DB_URI = 'sqlite:///' + TEST_DB_PATH


# =====================
# Engine and bound base
# =====================

@pytest.fixture(scope='session')
def sa_engine():
    return create_engine(TEST_DB_URI)


@pytest.fixture(scope='session')
def sa_declarative_base(sa_engine):
    return declarative_base(bind=sa_engine)


# ==================
# Database / Session
# ==================

@pytest.fixture(scope='session')
def sa_db(request,
          sa_declarative_base,
          sa_owner_model, sa_schedule_model, sa_news_model):
    # create tables
    sa_declarative_base.metadata.create_all()

    # clear tables
    def teardown():
        sa_declarative_base.metadata.drop_all()

    request.addfinalizer(teardown)


@pytest.fixture(scope='function')
def sa_session(request, sa_declarative_base, sa_db, sa_engine):
    session = sessionmaker(bind=sa_engine)()
    connection = sa_engine.connect()
    transaction = connection.begin()

    # rollback test transaction, close connection and remove session
    def teardown():
        transaction.rollback()
        connection.close()

    request.addfinalizer(teardown)

    return session
