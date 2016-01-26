from fixtures import *


def test_add_site(json_backend, site):
    assert(not json_backend.site_exists(site))
    json_backend.add_site(site)
    assert(json_backend.site_exists(site))


def test_delete_site(json_backend, site):
    json_backend.add_site(site)
    assert(json_backend.site_exists(site))
    json_backend.delete_site(site)
    assert(not json_backend.site_exists(site))


def test_get_site(json_backend, site):
    json_backend.add_site(site)
    assert(site == json_backend.get_site(site.url))


def test_store_valid(path, json_backend, valid_store_json):
    path.write('{"site": {1: {"url": 1}}, "news": {1: {"content": 2}}}')
    assert(not json_backend.store_valid)
    path.write(valid_store_json)
    assert(json_backend.store_valid)


def test_add_news(json_backend, news):
    assert(not json_backend.news_exists(news.url))
    json_backend.add_news(news)
    assert(json_backend.news_exists(news.url))


def test_delete_news(json_backend, news):
    assert(not json_backend.news_exists(news.url))
    json_backend.add_news(news)
    assert(json_backend.get_news(news.url) == news)
    json_backend.delete_news(news)
    assert(not json_backend.news_exists(news))


def test_news_exists(json_backend, news):
    assert(not json_backend.news_exists(news))
    json_backend.add_news(news)
    assert(json_backend.news_exists(news))


def test_get_news(json_backend, news):
    assert(not json_backend.news_exists(news))
    assert(json_backend.get_news(news.url) is None)
    json_backend.add_news(news)
    assert(json_backend.get_news(news.url) == news)


def test_get_news_list(json_backend, news):
    assert(news not in json_backend.get_news_list())
    json_backend.add_news(news)
    assert(news in json_backend.get_news_list())


def test_get_urls(json_backend, news):
    json_backend.add_news(news)
    assert(news.url in json_backend.get_urls())
    assert(len(json_backend.get_urls()) == 1)
