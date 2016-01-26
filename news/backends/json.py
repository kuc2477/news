""":mod:`news.backends.json` --- JSON backend
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

JSON news store backend for news.

"""
from functools import partial, wraps

from tinydb import TinyDB, where

from . import BackendBase
from ..news import News
from ..site import Site
from ..exceptions import InvalidStoreSchemaError


STORE_PATH = '.NEWS_STORE.json'
STORE_SITE_COLUMN_TYPES = {
    'url': str
}
STORE_NEWS_COLUMN_TYPES = {
    'site': str,
    'src': (str, None),
    'url': str,
    'content': str,
    'title': (str, None),
    'image': (str, None),
    'description': (str, None)
}


# decorator to check database consistancy
def should_store_valid(f=None, default=None, error=True):
    if f is None:
        return partial(should_store_valid, default=default, error=error)

    # Set validity checked flag to True once the method passes validity test.
    # This will work as performance boost as method will bypass validity test
    # once the method has passed the test.
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if wrapper.validity_checked or self.store_valid:
            wrapper.validity_checked = True
            return f(self, *args, **kwargs)
        if default is None:
            raise InvalidStoreSchemaError
        else:
            return default

    wrapper.validity_checked = False

    return wrapper


class JSONBackend(BackendBase):
    def __init__(self, path=STORE_PATH, *args, **kwargs):
        self.path = path
        self._db = TinyDB(self.path)
        self._site_table = self._db.table('site')
        self._news_table = self._db.table('page')
        self._news_cache = {}

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
    def add_news(self, *news):
        for site in {n.site for n in news if not self.site_exists(n.site)}:
            self.add_site(site)

        for news in news:
            self._news_table.insert(news.to_json())

        self.invalidate_news_cache()

    @should_store_valid
    def delete_news(self, *news):
        for n in news:
            self._news_table.remove(where('url') == n.url)

        self.invalidate_news_cache()

    def news_exists(self, news):
        url = getattr(news, 'url', news)
        return self._news_table.get(where('url') == url)

    @should_store_valid
    def get_news(self, url):
        if url is None:
            return None

        if url in self._news_cache:
            # use cached news if exists
            return self._news_cache[url]

        try:
            p = self._news_table.search(where('url') == url).pop()
        except IndexError:
            # return None if news doesn't exist in the table
            return None
        else:
            site = Site(p['site'])
            src = self.get_news(p['src'])
            content = p['content']

            # build news from backend
            news = News(site, src, url, content)
            self._news_cache[url] = news
            return news

    @should_store_valid
    def get_news_list(self, site=None):
        # Site should be either url itself or `~news.site.Site` instance.
        assert(isinstance(site, (str, Site)) or site is None)

        ps = self._news_table.all()
        if site is not None:
            ps = [p for p in ps if
                  (p['site'] == site if isinstance(site, str) else
                   p['site'] == site.url)]

        return [self.get_news(u) for u in [p['url'] for p in ps]]

    @property
    def store_valid(self):
        # alias
        SITE_COLTYPES = STORE_SITE_COLUMN_TYPES
        NEWS_COLTYPES = STORE_NEWS_COLUMN_TYPES

        try:
            return all(
                [_valid(s, SITE_COLTYPES) for s in self._site_table.all()] +
                [_valid(p, NEWS_COLTYPES) for p in self._news_table.all()]
            )
        except (TypeError, ValueError):
            return False

    def invalidate_news_cache(self):
        self._news_cache = {}


def _valid(e, schema):
    if not isinstance(e, dict):
        return False

    for name, types in schema.items():
        try:
            valid = isinstance(e[name], types)
        except TypeError:
            nullable = None in types
            types = tuple([t for t in types if t is not None])
            valid = isinstance(e[name], types) or (
                nullable and e[name] is None)
        if not valid:
            return False
    return True
