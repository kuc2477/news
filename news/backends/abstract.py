""":mod:`news.backends.abstract` --- Contains abstract backend class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides common interface that should be implemented by orm specific backends.

"""
import collections


class AbstractBackend(object):
    """
    Abstract news backend that should be implemented in orm specific ways.

    :param owner_class: Owner class to use with backend.
    :type owner_class: Implementation of `~news.models.AbstractModel`.
    :param schedule_class: Schedule class to use with backend.
    :type schedule_class: Implementation of `~news.models.AbstractSchedule`.
    :param news_class: News class to use with backend.
    :type news_class: Implementation of `~news.models.AbstractNews`.

    """

    combinations = {}

    def __init__(self, owner_class=None, schedule_class=None, news_class=None, 
                 *args, **kwargs):
        self.owner_class = owner_class
        self.schedule_class = schedule_class
        self.news_class = news_class

    @classmethod
    def create_backend(
            cls, owner_class=None, schedule_class=None, news_class=None,
            *args, **kwargs):
        # make combination of model classes and check if same type of backend
        # with same combination of model classes ever been instantiated or
        # not.
        C = collections.namedtuple('Combination', 'owner schedule news')
        c = C(owner=owner_class, schedule=schedule_class, news=news_class)

        if c in cls.combinations:
            return cls.combinations[c]
        else:
            return cls(owner_class=owner_class,
                       schedule_class=schedule_class,
                       news_class=news_class,
                       *args, **kwargs)

    def get_news(self, owner=None, url=None):
        """
        Should retrive a news for owner from backend.

        :param owner: Owner of the news.
        :type owner: :attr: `owner_class`
        :param url: Url of the news.
        :type url: :class:`str`
        :return: Owner's news with given url.
        :rtype: :attr: `news_class`

        """
        raise NotImplementedError

    def get_news_list(self, owner, root_url):
        """
        Should retrieve  a list of news for owner from backend.

        :param owner: Owner of the news.
        :type owner: :attr:`owner_class`
        :param root_url: Url of the root news.
        :type root_url: :class:`str`
        :return: A list of news under the given root url.
        :rtype: :class:`list`

        """
        raise NotImplementedError

    def save_news(self, *news):
        """
        Should save news to the backend.

        :param news: News to save.
        :type news: :attr:`news_class`

        """
        raise NotImplementedError

    def delete_news(self, *news):
        """
        Delete news in the backend.

        :param news: News to delete.
        :type news: :attr:`news_class`

        """
        raise NotImplementedError

    def news_exists(self, owner, url):
        """
        Should check existance of the news in the backend.

        :param owner: Owner of the news.
        :type owner: :attr:`owner_class`
        :param url: Url of the news.
        :type url: :class:`str`
        :return: Whether the news exists in the backend or not.
        :rtype: :class:`bool`

        """
        return self.get_news(owner, url) is not None

    def get_schedule(owner, url):
        """
        Should retrieve a schedule meta for owner from the backend.

        :param owner: Owner of the schedule meta.
        :type owner: :attr:`owner_class`
        :return: Owner's schedule meta with given url.
        :rtype: :attr:`schedule_meta_class`

        """
        raise NotImplementedError

    def get_schedules(owner):
        """
        Should retrieve a list of schedule meta for owner from backend.

        :param owner: Owner of the schedule meta list.
        :type owner: :attr:`schedule_meta_class`
        :return: A list of owner's schedule meta.
        :rtype: :class:`list`

        """

        raise NotImplementedError

    def schedule_exists(self, owner, url):
        """
        Should check existance of the schedule meta in the backend.

        :param owner: Owner of the schedule meta.
        :type owner: :attr:`schedule_meta_class`
        :param url: Url of the schedule meta.
        :type url: :class:`str`
        :return: Whether the schedule meta exists in the backend or not.
        :rtype: :class:`bool`

        """
        return self.get_schedule(owner, url) is not None

    def set_post_save_listener(self, listener):
        """Should register post save listener"""
        raise NotImplementedError

    def set_post_delete_listener(self, listener):
        """Should register post save listener"""
        raise NotImplementedError
