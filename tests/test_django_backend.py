import pytest

from fixtures import *


@pytest.mark.django_db
def test_add_site(django_backend, site):
    assert(not django_backend.site_exists(site))
    django_backend.add_site(site)
    assert(django_backend.site_exists(site))


@pytest.mark.django_db
def test_delete_site(django_backend, site):
    django_backend.add_site(site)
    assert(django_backend.site_exists(site))
    django_backend.delete_site(site)
    assert(not django_backend.site_exists(site))


@pytest.mark.django_db
def test_get_site(django_backend, site):
    django_backend.add_site(site)
    assert(django_backend.get_site(site.url) == site)


@pytest.mark.django_db
def test_add_news(django_backend, news):
    assert(not django_backend.news_exists(news))
    django_backend.add_news(news)
    assert(django_backend.news_exists(news))


@pytest.mark.django_db
def test_delete_news(django_backend, news):
    django_backend.add_news(news)
    assert(django_backend.news_exists(news))
    django_backend.delete_news(news)
    assert(not django_backend.news_exists(news))


@pytest.mark.django_db
def test_news_exists(django_backend, news):
    assert(not django_backend.news_exists(news))
    django_backend.add_news(news)
    assert(django_backend.news_exists(news))
    django_backend.delete_news(news)
    assert(not django_backend.news_exists(news))


@pytest.mark.django_db
def test_get_news(django_backend, news):
    django_backend.add_news(news)
    assert(news == django_backend.get_news(news.url))


@pytest.mark.django_db
def test_get_news_list(django_backend, news):
    django_backend.add_news(news)
    assert(news in django_backend.get_news_list())


@pytest.mark.django_db
def test_get_urls(django_backend, news):
    django_backend.add_news(news)
    assert(news.url in django_backend.get_urls())
    assert(len(django_backend.get_urls()) == 1)
