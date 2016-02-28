import pytest


@pytest.fixture
def django_owner_class():
    from django.contrib.auth import get_user_model
    usermodel = get_user_model()
    return usermodel


@pytest.fixture
def django_schedule_class():
    from news.models.django import Schedule
    return Schedule


@pytest.fixture
def django_news_class():
    from news.models.django import News
    return News


@pytest.fixture
def django_owner(django_owner_class):
    owner = django_owner_class(
        username='testuser',
        password='testpassword',
        email='testemail@test.com',
        first_name='testfirstname',
        last_name='testlastname'
    )
    owner.save()
    return owner


@pytest.fixture
def django_schedule(db, django_schedule_class, django_owner, url_root):
    schedule = django_schedule_class(owner=django_owner, url=url_root)
    schedule.save()
    return schedule


@pytest.fixture
def django_root_news(db, django_news_class, django_schedule,
                     url_root, content_root):
    news = django_news_class(
        schedule=django_schedule,
        url=url_root,
        content=content_root
    )
    news.save()
    return news


@pytest.fixture
def django_news(db, django_news_class, django_schedule, django_root_news,
                url_child, content_child):
    news = django_news_class(
        schedule=django_schedule,
        src=django_root_news,
        url=url_child,
        content=content_child
    )
    news.save()
    return news
