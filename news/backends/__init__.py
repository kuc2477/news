""":mod:`news.backends` --- Backend abstract base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide common interface for news backend implementations.

"""
import abc


class SignletoneBackendMixin(object):
    """
    Mixin for singletone backend implementations.

    """

    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance


class BackendBase(metaclass=abc.ABCMeta):
    """
    Abstract base class of news backend.

    """

    #: Implementation of `~news.models.AbstractOwnerMixin`
    owner_class = NotImplemented

    #: Implementation of `~news.models.AbstractNewsMixin`
    news_class = NotImplemented

    #: Implementation of `~news.models.AbstractScheduleMetaMixin`
    schedule_meta_class = NotImplemented

    @abc.abstractmethod
    def get_news(self, owner, url):
        """
        Retrieve a news for owner from backend.

        :param owner: Owner of the news.
        :type owner: :attr: `owner_class`
        :param url: Url of the news.
        :type url: :class:`str`
        :return: Owner's news with given url.
        :rtype: :attr: `news_class`

        """
        return NotImplemented

    @abc.abstractmethod
    def get_news_list(self, owner, root_url):
        """
        Retrieve a list of news for owner from backend.

        :param owner: Owner of the news.
        :type owner: :attr:`owner_class`
        :param root_url: Url of the root news.
        :type root_url: :class:`str`
        :return: A list of news under the given root url.
        :rtype: :class:`list`

        """
        return NotImplemented

    @abc.abstractmethod
    def add_news(self, *news):
        """
        Add news to the backend.

        :param news: News to add.
        :type news: :attr:`news_class`

        .. note:: News won't be added if a news of both same owner and url
            already exists in the backend.

        """
        return NotImplemented

    @abc.abstractmethod
    def update_news(self, *news):
        """
        Update news in the backend.

        :param news: News to update.
        :type news: :attr:`news_class`

        """
        return NotImplemented

    @abc.abstractmethod
    def delete_news(self, *news):
        """
        Delete news in the backend.

        :param news: News to delete.
        :type news: :attr:`news_class`

        """
        return NotImplemented

    def news_exists(self, owner, url):
        """
        Check existance of the news in the backend.

        :param owner: Owner of the news.
        :type owner: :attr:`owner_class`
        :param url: Url of the news.
        :type url: :class:`str`
        :return: Whether the news exists in the backend or not.
        :rtype: :class:`bool`

        """
        return self.get_news(owner, url) is not None

    @abc.abstractmethod
    def get_schedule_meta(owner, url):
        """
        Retrieve a schedule meta for owner from the backend.

        :param owner: Owner of the schedule meta.
        :type owner: :attr:`owner_class`
        :return: Owner's schedule meta with given url.
        :rtype: :attr:`schedule_meta_class`

        """
        return NotImplemented

    @abc.abstractmethod
    def get_schedule_meta_list(owner):
        """
        Retrieve a list of schedule meta for owner from backend.

        :param owner: Owner of the schedule meta list.
        :type owner: :attr:`schedule_meta_class`
        :return: A list of owner's schedule meta.
        :rtype: :class:`list`

        """

        return NotImplemented

    def schedule_meta_exists(self, owner, url):
        """
        Check existance of the schedule meta in the backend.

        :param owner: Owner of the schedule meta.
        :type owner: :attr:`schedule_meta_class`
        :param url: Url of the schedule meta.
        :type url: :class:`str`
        :return: Whether the schedule meta exists in the backend or not.
        :rtype: :class:`bool`

        """
        return self.get_schedule_meta(owner, url) is not None
