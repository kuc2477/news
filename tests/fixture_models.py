import pytest
from django.contrib.auth import get_user_model
from sqlalchemy import (
    Column,
    Integer
)
from news.models import django
from news.models import sqlalchemy as sa


# =============
# Django models
# =============

@pytest.fixture(scope='session')
def django_owner_model():
    return get_user_model()


@pytest.fixture(scope='session')
def django_abc_schedule(django_owner_model):
    return django.create_abc_schedule(django_owner_model)


@pytest.fixture(scope='session')
def django_abc_news(django_schedule_model):
    return django.create_abc_news(django_schedule_model)


@pytest.fixture(scope='session')
def django_schedule_model(django_abc_schedule):
    return django.create_schedule(django_abc_schedule)


@pytest.fixture(scope='session')
def django_news_model(django_abc_news):
    return django.create_news(django_abc_news)


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
def sa_schedule_model(sa_abc_schedule, sa_declarative_base):
    return sa.create_schedule(sa_abc_schedule, sa_declarative_base)


@pytest.fixture(scope='session')
def sa_news_model(sa_abc_news, sa_declarative_base):
    return sa.create_news(sa_abc_news, sa_declarative_base)


# ======================
# Django model instances
# ======================

@pytest.fixture
def django_owner(django_owner_model):
    owner = django_owner_model(
        username='testuser',
        password='testpassword',
        email='testemail@test.com',
        first_name='testfirstname',
        last_name='testlastname'
    )
    owner.save()
    return owner


@pytest.fixture
def django_schedule(db, django_schedule_model, django_owner, url_root):
    schedule = django_schedule_model(owner=django_owner, url=url_root)
    schedule.save()
    return schedule


@pytest.fixture
def django_root_news(db, django_news_model, django_schedule,
                     url_root, content_root):
    news = django_news_model(
        schedule=django_schedule,
        url=url_root,
        content=content_root
    )
    news.save()
    return news


@pytest.fixture
def django_news(db, django_news_model, django_schedule, django_root_news,
                url_child, content_child):
    news = django_news_model(
        schedule=django_schedule,
        src=django_root_news,
        url=url_child,
        content=content_child
    )
    news.save()
    return news


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
                 url_root, content_root):
    news = sa_news_model(schedule=sa_schedule, url=url_root,
                         content=content_root)
    sa_session.add(news)
    sa_session.commit()

    def teardown():
        sa_session.delete(news)
        sa_session.commit()
    request.addfinalizer(teardown)

    return news


@pytest.fixture
def sa_news(request, sa_session, sa_schedule, sa_root_news, sa_news_model,
            url_child, content_child):
    news = sa_news_model(
        schedule=sa_schedule, src=sa_root_news,
        url=url_child, content=content_child
    )
    sa_session.add(news)
    sa_session.commit()

    def teardown():
        sa_session.delete(news)
        sa_session.commit()
    request.addfinalizer(teardown)

    return news
