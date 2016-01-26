""":mod:`news.backends.sqlalchemy` --- SQLAlchemy backend

SQLAlchemy news store backend.

"""
from . import BackendBase


class SQLAlchemyBackend(BackendBase):
    _insteance = None

    def __new__(cls, *args, **kwargs):
        if not cls._insteance:
            cls._insteance = super().__new__(cls, *args, **kwargs)
        return cls._insteance

    def add_site(self, site):
        pass

    def delete_site(self, site):
        pass

    def get_site(self, url):
        pass

    def add_news(self, *news):
        pass

    def delete_news(self, *news):
        pass

    def get_news(self, url):
        pass

    def get_news_list(self, site=None):
        pass
