from functools import wraps
import json

from news.exceptions import (
    StoreDoesNotExistError,
    InvalidStoreSchemaError
)

from fixtures import *


def test_store_exists(path, json_backend):
    assert(not json_backend.store_exists)
    path.write('{}')
    assert(json_backend.store_exists)

def test_store_empty(path, json_backend):
    assert(json_backend.store_empty)
    path.write('{}')
    assert(json_backend.store_empty)

def test_store_valid(path, json_backend, valid_store_json):
    path.write('{"1": 1}')
    assert(not json_backend.store_valid)
    path.write(valid_store_json)
    assert(json_backend.store_valid)

def test_create_store(path, json_backend):
    assert(not json_backend.store_exists)
    json_backend.create_store()
    assert(json_backend.store_exists)
    assert(json_backend.get_urls() == [])

def test_destroy_store(path, json_backend):
    assert(not json_backend.store_exists)
    json_backend.create_store()
    assert(json_backend.store_exists)
    json_backend.destroy_store()
    assert(not json_backend.store_exists)

def test_add_pages(json_backend, page):
    json_backend.create_store()
    assert(json_backend.store_empty)
    json_backend.add_pages(page)
    assert(not json_backend.store_empty)

def test_delete_pages(json_backend, page):
    json_backend.create_store()
    json_backend.add_pages(page)
    assert(not json_backend.store_empty)
    json_backend.delete_pages(page)
    assert(json_backend.store_empty)

def test_page_exists(json_backend, page):
    json_backend.create_store()
    assert(not json_backend.page_exists(page))
    json_backend.add_pages(page)
    assert(json_backend.page_exists(page))

def test_get_page(json_backend, page):
    json_backend.create_store()
    assert(not json_backend.page_exists(page))
    assert(json_backend.get_page(page.url) is None)
    json_backend.add_pages(page)
    assert(json_backend.get_page(page.url) == page)

def test_get_pages(json_backend, page):
    json_backend.create_store()
    json_backend.add_pages(page)
    assert(page in json_backend.get_pages())

def test_get_urls(json_backend, page):
    json_backend.create_store()
    json_backend.add_pages(page)
    assert(page.url in json_backend.get_urls())
    assert(len(json_backend.get_urls()) == 1)
