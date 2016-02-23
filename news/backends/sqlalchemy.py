""":mod:`news.backends.sqlalchemy` --- SQLAlchemy backend

SQLAlchemy news store backend.

"""
from . import AbstractBackend


class SQLAlchemyBackend(AbstractBackend):
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

    def get_schedule(self, owner, url):
        pass

    def get_schedule_list(self, owner):
        pass
