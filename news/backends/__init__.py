""":mod:`news.backends` --- Page backend abstract base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides common interface for multiple page backend implementations.

"""
import abc
from functools import wraps

from ..exceptions import (
    StoreDoesNotExistError,
    InvalidStoreSchemaError
)


STORE_COLUMN_TYPES = {
    'site_url': str,
    'src_url': (str, None)
    'url' : str,
    'content': str,
}


def should_store_exist(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.store_exists:
            raise StoreDoesNotExistError
        return f(self, *args, **kwargs)
    return wrapper

def should_store_valid(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.store_valid:
            raise InvalidStoreSchema
        return f(self, *args, **kwargs)
    return wrapper


class BackendBase(metaclass=abc.ABCMeta):
    """Abstract base class for page store backends.

    Provides common interface for schedule classes to interact with
    different page storage backends.

    :param site: The host site of the backend.
    :type site: :class:`news.site.Site`

    """

    @abc.abstractproperty
    def store_exists(self):
        return NotImplemented

    @abc.abstractproperty
    def store_empty(self):
        return NotImplemented

    @abc.abstractproperty
    def store_valid(self):
        return NotImplemented

    @abc.abstractmethod
    def create_store(self):
        return NotImplemented

    @abc.abstractmethod
    def destroy_store(self):
        return NotImplemented

    @abc.abstractmethod
    def add_pages(self, *pages):
        """Adds a page to the backend's store

        Note that won't be added if page already exists in the store. Page
        existance will be tested by :attr:`~news.page.Page.url` equality.

        """
        return NotImplemented

    @abc.abstractmethod
    def delete_pages(self, pages):
        """Deletes a page from the backend's store

        :param page: The page to delete.
        :type page: :class:`news.page.Page`
        :return: Result of the deletion.
        :rtype: :class:`bool`


        """
        return NotImplemented

    @abc.abstractmethod
    def page_exists(self, page):
        """Check existance of the page from the import backend's store

        :param page: The page to test existance.
        :type page: :class:`news.page.Page`
        :return: Whether the page exists in the page storage.
        :rtype: :class:`bool`

        """
        return NotImplemented

    @property
    def urls(self):
        """Returns urls of the stored pages.

        :return: urls of the stored pages.
        :rtype: :class:`list`

        """
        return [page.url for page in self.pages]
