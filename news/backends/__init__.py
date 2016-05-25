""":mod:`news.backends` --- News backends
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

News backends for schedule and news persistence.

"""
from .django import DjangoBackend
from .sqlalchemy import SQLAlchemyBackend
