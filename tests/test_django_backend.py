import pytest


@pytest.mark.django_db
def test_save_news(django_backend, django_schedule, django_news_class,
                   url, content):
    news = django_news_class(
        schedule=django_schedule,
        url=url,
        content=content
    )
    url = news.url
    owner = news.schedule.owner

    assert(not django_backend.news_exists(owner, url))
    django_backend.save_news(news)
    assert(django_backend.news_exists(owner, url))


@pytest.mark.django_db
def test_delete_news(django_backend, django_news):
    url = django_news.url
    owner = django_news.schedule.owner

    assert(django_backend.news_exists(owner, url))
    django_backend.delete_news(django_news)
    assert(not django_backend.news_exists(owner, url))


@pytest.mark.django_db
def test_news_exists(django_backend, django_news):
    url = django_news.url
    owner = django_news.schedule.owner

    assert(django_backend.news_exists(owner, url))
    django_backend.delete_news(django_news)
    assert(not django_backend.news_exists(owner, url))


@pytest.mark.django_db
def test_get_news(django_backend, django_news):
    url = django_news.url
    owner = django_news.schedule.owner

    assert(django_news == django_backend.get_news(owner, url))


@pytest.mark.django_db
def test_get_news_list(django_backend, django_news):
    assert(django_news in django_backend.get_news_list())
