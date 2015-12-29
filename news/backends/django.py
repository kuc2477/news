""":mod:`news.backends.django` --- Django ORM backend

Django ORM page store backend for news.

"""
from django.db import connection
from django.db import models

from . import (
    BackendBase,
    should_store_exist,
    should_store_valid,
    STORE_COLUMN_TYPES,
    STORE_TABLE_NAME
)

from ..page import Page
from ..site import Site
from ..exceptions import InvalidStoreSchemaError


URL_MAX_LENGTH = 300


class DjangoBackend(BackendBase):
    def __init__(self, settings):
        self.settings = settings

    @property
    def store_exists(self):
        cursor = connection.cursor()
        return self.table in connection.introspection.get_table_list(cursor)


class Site(models.Model):
    url = models.CharField(max_length=URL_MAX_LENGTH)


class Page(models.Model):
    url = models.CharField(max_length=URL_MAX_LENGTH)
    site = models.ForeignKey(Site, related_name='pages', db_index=True)
    src = models.ForeignKey('self', null=True, blank=True,
                            related_name='children', db_index=True)
    content = models.TextField()
