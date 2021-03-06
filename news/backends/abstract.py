""":mod:`news.backends.abstract` --- Backend interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides abstract backend interfaces that should be implemented.

"""
import collections


class AbstractBackend(object):
    """Abstract news backend that should be implemented in orm specific ways

    :param schedule_model: Schedule class to use with backend.
    :type schedule_model: Implementation of
        :class:`~news.models.AbstractSchedule`.
    :param news_model: News class to use with backend.
    :type news_model: Implementation of
        :class:`~news.models.abstract.AbstractNews`.

    """
    combinations = {}

    def __init__(self, schedule_model=None, news_model=None, *args, **kwargs):
        self.schedule_model = self.Schedule = schedule_model
        self.news_model = self.News = news_model

    @classmethod
    def create_backend(
            cls, schedule_model=None, news_model=None, *args, **kwargs):
        # make combination of model classes and check if same type of backend
        # with same combination of model classes ever been instantiated or
        # not.
        C = collections.namedtuple('Combination', 'schedule news')
        c = C(schedule=schedule_model, news=news_model)

        if c in cls.combinations:
            return cls.combinations[c]
        else:
            return cls(schedule_model=schedule_model, news_model=news_model,
                       *args, **kwargs)

    def get_news(self, id):
        """Should retrive a news with given id.

        :param id: Id of the news.
        :type id: :attr: `int`
        :return: News of the given id.
        :rtype: :attr: `news_model`

        """
        raise NotImplementedError

    def get_news_by(self, owner, url):
        """Should return a news for owner from backend.

        :param owner: Owner of the news.
        :type owner: :attr:`owner_model` of :attr:`schedule_model`
        :param url: Url of the news.
        :type url: :class:`str`

        """
        raise NotImplementedError

    def get_news_list(self, owner, root_url):
        """Should retrieve  a list of news for owner from backend.

        :param owner: Owner of the news.
        :type owner: :attr:`owner_model` of :attr:`schedule_model`
        :param root_url: Url of the root news.
        :type root_url: :class:`str`
        :return: A list of news under the given root url.
        :rtype: :class:`list`

        """
        raise NotImplementedError

    def save_news(self, *news):
        """Should save news to the backend.

        :param news: News to save.
        :type news: :attr:`news_model`

        """
        raise NotImplementedError

    def delete_news(self, *news):
        """Delete news in the backend.

        :param news: News to delete.
        :type news: :attr:`news_model`

        """
        raise NotImplementedError

    def news_exists(self, id):
        """Should check existance of the news in the backend.

        :param id: Id of the news.
        :type id: :class:`int`
        :return: Whether the news exists in the backend or not.
        :rtype: :class:`bool`

        """
        return self.get_news(id) is not None

    def news_exists_by(self, owner, url):
        return self.get_news_by(owner, url) is not None

    def get_schedule(owner, url):
        """Should retrieve a schedule for owner from the backend.

        :param owner: Owner of the schedule
        :type owner: :attr:`owner` of :attr:`schedule_model`
        :return: Owner's schedule with given url.
        :rtype: :attr:`schedule_model`

        """
        raise NotImplementedError

    def get_schedules(owner):
        """Should retrieve a list of schedule for owner from backend.

        :param owner: Owner of the schedules.
        :type owner: :attr:`owner` of :attr:`schedule_model`
        :return: A list of owner's schedule.
        :rtype: :class:`list`

        """
        raise NotImplementedError

    def schedule_exists(self, id):
        """Should check existance of the schedule in the backend.

        :param owner: Owner of the schedule
        :type owner: :attr:`owner` of :attr:`schedule_model`
        :param url: Url of the schedule .
        :type url: :class:`str`
        :return: Whether the schedule exists in the backend or not.
        :rtype: :class:`bool`

        """
        return self.get_schedule(id) is not None
