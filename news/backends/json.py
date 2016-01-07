""":mod:`news.backends.json` --- JSON backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

JSON page store backend for news.

"""
import os
import json
from functools import partial, wraps
from itertools import repeat

from tinydb import TinyDB, where

from . import BackendBase
from ..page import Page
from ..site import Site
from ..exceptions import InvalidStoreSchemaError


STORE_PATH = '.NEWS_STORE.json'
STORE_SITE_COLUMN_TYPES = {
    'url': str
}
STORE_PAGE_COLUMN_TYPES = {
    'site': str,
    'src': (str, None),
    'url' : str,
    'content': str,
}


# decorator to check database consistancy
def should_store_valid(f=None, default=None, error=True):
    if f is None:
        return partial(should_store_valid, default=default, error=error)

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.store_valid:
            return f(self, *args, **kwargs)
        if default is None:
            raise InvalidStoreSchemaError
        else:
            return default
    return wrapper


class JSONBackend(BackendBase):
    def __init__(self, path=STORE_PATH, *args, **kwargs):
        self.path = path
        self._db = TinyDB(self.path)
        self._site_table = self._db.table('site')
        self._page_table = self._db.table('page')
        self._page_cache = {}

    @should_store_valid
    def add_site(self, site):
        self._site_table.insert(site.to_json())

    @should_store_valid
    def delete_site(self, site):
        self._site_table.remove(where('url') == site.url)

    @should_store_valid
    def get_site(self, url):
        s = self._site_table.get(where('url') == url)
        return Site(s['url']) if s is not None else None

    @should_store_valid
    def add_pages(self, *pages):
        for page in pages:
            self._page_table.insert(page.to_json())

    @should_store_valid
    def delete_pages(self, *pages):
        for page in pages:
            self._page_table.remove(where('url') == page.url)

    def page_exists(self, page):
        url = getattr(page, 'url', page)
        return self._page_table.get(where('url') == url)

    @should_store_valid
    def get_page(self, url):
        if url is None:
            return None

        if url in self._page_cache:
            # use cached page if exists
            return self._page_cache[url]

        try:
            p = self._page_table.search(where('url') == url).pop()
        except IndexError:
            # return None if page doesn't exist in the table
            return None
        else:
            site = Site(p['site'])
            src = self.get_page(p['src'])
            content = p['content']

            # build page from backend
            page = Page(site, src, url, content)
            self._page_cache[url] = page
            return page


    @should_store_valid
    def get_pages(self, site=None):
        # Site should be either url itself or `~news.site.Site` instance.
        assert(isinstance(site, (str, Site)) or site is None)

        ps = self._page_table.all()
        if site is not None:
            ps = [p for p in ps if
                  (p['site'] == site if isinstance(site, str) else
                   p['site'] == site.url)]

        return [self.get_page(u) for u in [p['url'] for p in ps]]

    @property
    def store_valid(self):
        try:
            return all(
                [_valid(s, STORE_SITE_COLUMN_TYPES) for s in self._site_table.all()] +
                [_valid(p, STORE_PAGE_COLUMN_TYPES) for p in self._page_table.all()]
            )
        except (TypeError, ValueError):
            return False

    def invalidate_page_cache(self):
        self._page_cache = {}


def _valid(e, schema):
    if not isinstance(e, dict):
        return False

    for name, types in schema.items():
        try:
            valid = isinstance(e[name], types)
        except TypeError:
            nullable = None in types
            types = tuple([t for t in types if t is not None])
            valid = isinstance(e[name], types) or (nullable and e[name] is None)
        if not valid:
            return False
    return True
