""":mod:`news.backends.sqlalchemy` --- SQLAlchemy backend

SQLAlchemy page store backend for news.

"""
from . import BackendBase


class SQLAlchemyBackend(BackendBase):
    _insteance = None

    def __new__(cls, *args, **kwargs):
        if not cls._insteance:
            cls._insteance = super().__new__(cls, *args, **kwargs)
        return cls._insteance
