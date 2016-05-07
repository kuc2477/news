""":mod:`news.backends` --- Abstract News backend interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides common interface that should be implemented by orm specific backends.

"""
import collections


class AbstractBackend(object):
    """
    Abstract news backend that should be implemented in orm specific ways.

    :param owner_model: Owner class to use with backend.
    :type owner_model: Implementation of :class:`~news.models.AbstractModel`.
    :param schedule_model: Schedule class to use with backend.
    :type schedule_model: Implementation of
        :class:`~news.models.AbstractSchedule`.
    :param news_model: News class to use with backend.
    :type news_model: Implementation of :class:`~news.models.AbstractNews`.

    """

    combinations = {}

    def __init__(self, owner_model=None, schedule_model=None, news_model=None,
                 *args, **kwargs):
        self.owner_model = self.Owner = owner_model
        self.schedule_model = self.Schedule = schedule_model
        self.news_model = self.News = news_model

    @classmethod
    def create_backend(
            cls, owner_model=None, schedule_model=None, news_model=None,
            *args, **kwargs):
        # make combination of model classes and check if same type of backend
        # with same combination of model classes ever been instantiated or
        # not.
        C = collections.namedtuple('Combination', 'owner schedule news')
        c = C(owner=owner_model, schedule=schedule_model, news=news_model)

        if c in cls.combinations:
            return cls.combinations[c]
        else:
            return cls(owner_model=owner_model,
                       schedule_model=schedule_model,
                       news_model=news_model,
                       *args, **kwargs)

    def get_news(self, id):
        """
        Should retrive a news with given id.

        :param id: Id of the news.
        :type id: :attr: `int`
        :return: News of the given id.
        :rtype: :attr: `news_model`

        """
        raise NotImplementedError

    def get_news_by(self, owner, url):
        """
        Should return a news for owner from backend.

        :param owner: Owner of the news.
        :type owner: :attr:`owner_model`
        :param url: Url of the news.
        :type url: :class:`str`

        """
        raise NotImplementedError

    def get_news_list(self, owner, root_url):
        """
        Should retrieve  a list of news for owner from backend.

        :param owner: Owner of the news.
        :type owner: :attr:`owner_model`
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
        :type news: :attr:`news_model`

        """
        raise NotImplementedError

    def delete_news(self, *news):
        """
        Delete news in the backend.

        :param news: News to delete.
        :type news: :attr:`news_model`

        """
        raise NotImplementedError

    def news_exists(self, id):
        """
        Should check existance of the news in the backend.

        :param id: Id of the news.
        :type id: :class:`int`
        :return: Whether the news exists in the backend or not.
        :rtype: :class:`bool`

        """
        return self.get_news(id) is not None

    def news_exists_by(self, owner, url):
        return self.get_news_by(owner, url) is not None

    def get_schedule(owner, url):
        """
        Should retrieve a schedule for owner from the backend.

        :param owner: Owner of the schedule meta.
        :type owner: :attr:`owner_model`
        :return: Owner's schedule meta with given url.
        :rtype: :attr:`schedule_model`

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

    def schedule_exists(self, id):
        """
        Should check existance of the schedule meta in the backend.

        :param owner: Owner of the schedule meta.
        :type owner: :attr:`schedule_meta_class`
        :param url: Url of the schedule meta.
        :type url: :class:`str`
        :return: Whether the schedule meta exists in the backend or not.
        :rtype: :class:`bool`

        """
        return self.get_schedule(id) is not None
