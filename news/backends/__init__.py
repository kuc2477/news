""":mod:`news.backends` --- News backend abstract base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides common interface for multiple news backend implementations.

"""
import abc

from ..news import News


class BackendBase(metaclass=abc.ABCMeta):
    """Abstract base class for news store backends.

    Provides common interface for schedule classes to interact with
    different news storage backends.

    :param site: The host site of the backend.
    :type site: :class:`news.site.Site`

    """

    @abc.abstractmethod
    def add_news(self, *news):
        """Adds a news to the backend's store

        Note that won't be added if news already exists in the store.

        """
        return NotImplemented

    @abc.abstractmethod
    def update_news(self, *news):
        return NotImplemented

    @abc.abstractmethod
    def delete_news(self, *news):
        """Deletes a news from the backend's store

        :param news: The news to delete.
        :type news: :class:`news.news.News`
        :return: Result of the deletion.
        :rtype: :class:`bool`


        """
        return NotImplemented

    @abc.abstractmethod
    def get_news(self, url):
        """Returns a stored news.

        :param url: The url of the news.
        :type url: :class:`str`
        :return: stored news.
        :rtype: :class:`news.news.News`

        """
        return NotImplemented

    @abc.abstractmethod
    def get_news_list(self, site=None):
        """Returns stored newss of the site.

        :param site: Site or site url of the newss.
        :type site: :class:`news.site.Site` or :class:`str`
        :return: newss of the site.
        :rtype: :class:`list`

        """
        return NotImplemented

    def news_exists(self, news):
        """Check existance of the news from the backend's store

        :param news: News or url to test existance.
        :type news: :class:`news.news.News` or :class:`str`
        :return: Whether the news exists in the news storage.
        :rtype: :class:`bool`

        """
        return self.get_news(
            news.url if isinstance(news, News) else news
        ) is not None

    def get_urls(self, site=None):
        """Returns stored urls of the site.

        :param site: Site or site url of the newss.
        :type site: :class:`news.site.Site` or :class:`str`
        :return: urls of the site newss.
        :rtype: :class:`list`

        """
        return [news.url for news in self.get_news_list(site)]

    @abc.abstractmethod
    def add_schedule_meta(*metas):
        return NotImplemented

    @abc.abstractmethod
    def update_schedule_meta(*metas):
        return NotImplemented

    @abc.abstractmethod
    def delete_schedule_meta(*metas):
        return NotImplemented

    @abc.abstractmethod
    def get_schedule_meta(owner, url):
        return NotImplemented

    @abc.abstractmethod
    def get_schedule_metas(owner_or_url):
        return NotImplemented

    def schedule_meta_exists(self, owner, url):
        return self.get_schedule_meta(owner, url) is not None
