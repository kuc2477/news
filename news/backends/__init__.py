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




class BackendBase(metaclass=abc.ABCMeta):
    """Abstract base class for page store backends.

    Provides common interface for schedule classes to interact with
    different page storage backends.

    :param site: The host site of the backend.
    :type site: :class:`news.site.Site`

    """

    @abc.abstractmethod
    def add_pages(self, *pages):
        """Adds a page to the backend's store

        Note that won't be added if page already exists in the store. Page
        existance will be tested by :attr:`~news.page.Page.url` equality.

        """
        return NotImplemented

    @abc.abstractmethod
    def delete_pages(self, *pages):
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

        :param page: Page or url to test existance.
        :type page: :class:`news.page.Page` or :class:`str`
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
