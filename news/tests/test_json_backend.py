from functools import wraps

import pytest

from .fixtures import *
from ..exceptions import (
    StoreDoesNotExistError,
    InvalidStoreSchemaError
)


def test_store_exists(path, backend):
    assert(not backend.store_exists)
    path.write('[]')
    assert(backend.store_exists)

def test_store_empty(path, backend):
    assert(backend.store_empty)
    path.write('[]')
    assert(backend.store_empty)

def test_store_valid(path, backend):
    with pytest.raises(StoreDoesNotExistError):
        backend.store_valid

    path.write('{"1": "1"}')
    assert(not backend.store_valid)

    path.write('[]')
    assert(backend.store_valid)

def test_create_store(path, backend):
    assert(not backend.store_exists)
    backend.create_store()
    assert(backend.store_exists)
    assert(backend.urls == [])

def test_destroy_store(path, backend):
    assert(not backend.store_exists)
    backend.create_store()
    assert(backend.store_exists)
    backend.destroy_store()
    assert(not backend.store_exists)

def test_add_pages(backend, page):
    backend.create_store()
    assert(backend.store_empty)
    backend.add_pages(page)
    assert(not backend.store_empty)

def test_delete_pages(backend, page):
    backend.create_store()
    backend.add_pages(page)
    assert(not backend.store_empty)
    backend.delete_pages(page)
    assert(backend.store_empty)

def test_urls(backend, page):
    backend.create_store()
    backend.add_pages(page)
    assert(len(backend.urls) == 1)
