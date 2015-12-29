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
    STORE_PATH,
    STORE_COLUMN_TYPES
)

from ..page import Page
from ..site import Site
from ..exceptions import InvalidStoreSchemaError


class JSONBackend(BackendBase):
    def __init__(self, path=STORE_PATH, *args, **kwargs):
        self.path = path

    @property
    def store_exists(self):
        return os.path.exists(self.path)

    @property
    @should_store_exist(default=True, error=False)
    def store_valid(self):
        with open(self.path, 'r') as store_json:
            store = json.load(store_json)
            return isinstance(store, dict) and all([
                _valid(p) for u, p in store.items()
            ])

    @property
    @should_store_exist(default=True, error=False)
    @should_store_valid
    def store_empty(self):
        with open(self.path, 'r') as store_json:
            return len(json.load(store_json)) == 0

    def create_store(self):
        with open(self.path, 'w') as store_json:
            json.dump({}, store_json)

    def destroy_store(self):
        os.remove(self.path)

    def add_pages(self, *pages):
        # Create JSON store if doesn't exists or is not valid.
        if not self.store_exists or not self.store_valid:
            self.create_store()

        # Add pages to the store.
        with open(self.path, 'r+') as store_json:
            store = json.load(store_json)
            updated = store.copy()
            updated.update({
                page.url: page.to_json() for page in pages
            })

            _dump(updated, store_json)

    @should_store_exist
    @should_store_valid
    def delete_pages(self, *pages):
        # Delete pages from store.
        with open(self.path, 'r+') as store_json:
            store = json.load(store_json)
            updated = {u: p for u, p in store.items() if u not in [
                page.url for page in pages
            ]}

            _dump(updated, store_json)

        # Destroy JSON store if store is empty
        if self.store_empty:
            self.destroy_store()

    @should_store_exist(default=False, error=False)
    @should_store_valid
    def page_exists(self, page):
        with open(self.path, 'r') as store_json:
            if page is None:
                return None
            elif not isinstance(page, (str, Page)):
                raise TypeError

            store = json.load(store_json)

            return page in store.keys() if isinstance(page, str) else \
                page.url in store.keys()

    @should_store_exist(default=None, error=False)
    @should_store_valid
    def get_page(self, url):
        with open(self.path, 'r') as store_json:
            if not self.page_exists(url):
                return None

            p = json.load(store_json)[url]

            site = Site(p['site'], self)
            src = self.get_page(p['src'])

            return Page(site, p['url'], p['content'], src)

    @should_store_exist(default=[], error=False)
    @should_store_valid
    def get_pages(self, site=None):
        with open(self.path, 'r') as store_json:
            store = json.load(store_json)

            if site is not None:
                store = {u: p for u, p in store.items() if (
                         p['site'] == site.url if isinstance(site, Site) else
                         p['site'] == site)}

            return [self.get_page(u) for u, p in store.items()]


def _valid(p):
    if not isinstance(p, dict):
        return False

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
