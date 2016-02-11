""":mod:`news.backends` --- News backend abstract base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides common interface for multiple news backend implementations.

"""
import abc


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
    def get_news(self, root, url):
        """Returns a stored news.

        :param root: URL of the root news of the news.
        :type root: :class:`str`
        :param url: URL of the news.
        :type url: :class:`str`
        :return: stored news.
        :rtype: :class:`news.news.News`

        """
        return NotImplemented

    @abc.abstractmethod
    def get_news_list(self, root=None):
        """Returns stored newss of the site.

        :param root: URL of the root news of the news.
        :type root: :class:`str`
        :return: A list of news
        :rtype: :class:`list`

        """
        return NotImplemented

    def news_exists(self, root, url):
        """Check existance of the news from the backend's store

        :param: root: URL of the root news of the news.
        :type root: :class:`str`
        :param url: URL of the news.
        :type url: :class:`str`
        :return: Whether the news exists in the news storage.
        :rtype: :class:`bool`

        """
        return self.get_news(root, url) is not None

    def get_urls(self, root=None):
        """Returns stored urls of the site.

        :param root: Site or site url of the newss.
        :type root: :class:`str`
        :return: URLs of the news list from given root news.
        :rtype: :class:`list`

        """
        return [news.url for news in self.get_news_list(root)]

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
