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

    def add_news(self, *news):
        pass

    def update_news(self, *news):
        pass

    def delete_news(self, *news):
        pass

    def get_news(self, url):
        pass

    def get_news_list(self, url=None):
        pass

    def add_schedule_meta(self, *metas):
        pass

    def update_schedule_meta(self, meta):
        pass

    def delete_schedule_meta(self, *metas):
        pass

    def get_schedule_meta(self, owner, url):
        pass

    def get_schedule_metas(self, owner, url):
        pass
