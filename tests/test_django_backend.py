import pytest


@pytest.mark.django_db
def test_add_news(django_backend, django_news):
    news = django_news

    assert(not django_backend.news_exists(news))
    django_backend.add_news(news)
    assert(django_backend.news_exists(news))


@pytest.mark.django_db
def test_delete_news(django_backend, django_news):
    news = django_news

    django_backend.add_news(news)
    assert(django_backend.news_exists(news))
    django_backend.delete_news(news)
    assert(not django_backend.news_exists(news))


@pytest.mark.django_db
def test_news_exists(django_backend, django_news):
    news = django_news

    assert(not django_backend.news_exists(news))
    django_backend.add_news(news)
    assert(django_backend.news_exists(news))
    django_backend.delete_news(news)
    assert(not django_backend.news_exists(news))


@pytest.mark.django_db
def test_get_news(django_backend, django_news):
    django_backend.add_news(django_news)
    assert(news == django_backend.get_news(news.url))


@pytest.mark.django_db
def test_get_news_list(django_backend, django_news):
    django_backend.add_news(django_news)
    assert(news in django_backend.get_news_list())
