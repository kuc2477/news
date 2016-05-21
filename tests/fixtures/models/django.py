import pytest
from django.contrib.auth import get_user_model
from news.models import django


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
def django_schedule_model(django_abc_schedule, persister):
    return django.create_schedule(django_abc_schedule,
                                  persister=persister)


@pytest.fixture(scope='session')
def django_news_model(django_abc_news):
    return django.create_news(django_abc_news)


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
def django_root_news(db, django_news_model, django_schedule, url_root, 
                     author_root, title_root, content_root, summary_root):
    news = django_news_model(
        url=url_root,
        schedule=django_schedule,
        title=title_root,
        author=author_root,
        content=content_root,
        summary=summary_root,
    )
    news.save()
    return news


@pytest.fixture
def django_news(db, django_news_model, django_schedule, django_root_news,
                url_child, author_child, title_child, content_child, 
                summary_child):
    news = django_news_model(
        url=url_child,
        schedule=django_schedule,
        src=django_root_news,
        title=title_child,
        author=author_child,
        content=content_child,
        summary=summary_child,
    )
    news.save()
    return news
