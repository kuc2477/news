""":mod:`news.backends.json` --- JSON backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

JSON page store backend for news.

"""
import os
import json
from itertools import repeat

from . import (
    BackendBase,
    should_store_exist,
    should_store_valid,
    STORE_COLUMN_TYPES
)

from ..exceptions import InvalidStoreSchemaError


class JSONBackend(BackendBase):
    def __init__(self, path, *args, **kwargs):
        self.path = path

    @property
    def store_exists(self):
        return os.path.exists(self.path)

    @property
    def store_empty(self):
        if not self.store_exists:
            return True

        if not self.store_valid:
            raise InvalidStoreSchemaError

        with open(self.path, 'r') as store_json:
            return len(json.load(store_json)) == 0

    @property
    @should_store_exist
    def store_valid(self):
        with open(self.path, 'r') as store_json:
            store = json.load(store_json)
            return isinstance(store, list) and all([_valid(p) for p in store])


    def create_store(self):
        with open(self.path, 'w') as store_json:
            json.dump([], store_json)

    def destroy_store(self):
        os.remove(self.path)

    def add_pages(self, *pages):
        # Create JSON store if doesn't exists or is not valid.
        if not self.store_exists or not self.store_valid:
            self.create_store()
        # Add pages to the store.
        with open(self.path, 'r+') as store_json:
            store = json.load(store_json)
            updated = store + [page.to_json() for page in pages]

            _dump(updated, store_json)

    @should_store_exist
    @should_store_valid
    def delete_pages(self, *pages):
        # Delete pages from store.
        with open(self.path, 'r+') as store_json:
            store = json.load(store_json)
            updated = [p for p in store if p['url'] not in
                       [page.url for page in pages]]

            _dump(updated, store_json)

        # Destroy JSON store if store is empty
        if self.store_empty:
            self.destroy_store()

    def page_exists(self, page):
        with open(self.path, 'r') as store_json:
            store = json.load(store_json)
            return page.url in [p['url'] for p in store]

    @property
    def urls(self):
        if not self.store_exists:
            return []

        with open(self.path, 'r') as store_json:
            store = json.load(store_json)
            return [p['url'] for p in store]


def _valid(p):
    for name, types in STORE_COLUMN_TYPES.items():
        try:
            valid = isinstance(p[name], types)

        except TypeError:
            nullable = None in types
            types = tuple([t for t in types if t is not None])
            valid = isinstance(p[name], types) or (nullable and p[name] is None)

        if not valid:
            return False
    return True

def _dump(store, store_json):
    store_json.seek(0)
    json.dump(store, store_json)
    store_json.truncate()
