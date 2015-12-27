""":mod:`news.backends` --- Page backend abstract base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides common interface for multiple page backend implementations.

"""
import abc
from functools import wraps
from functools import partial

from ..exceptions import (
    StoreDoesNotExistError,
    InvalidStoreSchemaError
)


STORE_TABLE_NAME = 'news_page'
STORE_COLUMN_TYPES = {
    'site': str,
    'src': (str, None),
    'url' : str,
    'content': str,
}


def should_store_exist(f=None, default=None, error=True):
    if f is None:
        return partial(should_store_exist, default=default, error=error)

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.store_exists:
            if error:
                raise StoreDoesNotExistError
            else:
                return default
        return f(self, *args, **kwargs)
    return wrapper

def should_store_valid(f=None, default=None, error=True):
    if f is None:
        return partial(should_store_valid, default=default, error=error)

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.store_valid:
            if default is None:
                raise InvalidStoreSchemaError
            else:
                return default
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
    def store_valid(self):
        return NotImplemented

    @abc.abstractproperty
    def store_empty(self):
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

    @abc.abstractmethod
    def get_page(self, url):
        """Returns a stored page.

        :param url: The url of the page.
        :type url: :class:`str`
        :return: stored page.
        :rtype: :class:`news.page.Page`

        """
        return NotImplemented

    @abc.abstractmethod
    def get_pages(self, site=None):
        """Returns stored pages of the site.

        :param site: Site or site url of the pages.
        :type site: :class:`news.site.Site` or :class:`str`
        :return: pages of the site.
        :rtype: :class:`list`

        """
        return NotImplemented

    def get_urls(self, site=None):
        """Returns stored urls of the site.

        :param site: Site or site url of the pages.
        :type site: :class:`news.site.Site` or :class:`str`
        :return: urls of the site pages.
        :rtype: :class:`list`

        """
        return [page.url for page in self.get_pages(site)]
