from functools import wraps
import json

from news.exceptions import (
    StoreDoesNotExistError,
    InvalidStoreSchemaError
)

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
    path.write('{"site": {1: {"url": 1}}, "page": {1: {"content": 2}}}')
    assert(not json_backend.store_valid)
    path.write(valid_store_json)
    assert(json_backend.store_valid)

def test_add_pages(json_backend, page):
    assert(not json_backend.page_exists(page.url))
    json_backend.add_pages(page)
    assert(json_backend.page_exists(page.url))

def test_delete_pages(json_backend, page):
    assert(not json_backend.page_exists(page.url))
    json_backend.add_pages(page)
    assert(json_backend.get_page(page.url) == page)
    json_backend.delete_pages(page)
    assert(not json_backend.page_exists(page))

def test_page_exists(json_backend, page):
    assert(not json_backend.page_exists(page))
    json_backend.add_pages(page)
    assert(json_backend.page_exists(page))

def test_get_page(json_backend, page):
    assert(not json_backend.page_exists(page))
    assert(json_backend.get_page(page.url) is None)
    json_backend.add_pages(page)
    assert(json_backend.get_page(page.url) == page)

def test_get_pages(json_backend, page):
    assert(not page in json_backend.get_pages())
    json_backend.add_pages(page)
    assert(page in json_backend.get_pages())

def test_get_urls(json_backend, page):
    json_backend.add_pages(page)
    assert(page.url in json_backend.get_urls())
    assert(len(json_backend.get_urls()) == 1)
