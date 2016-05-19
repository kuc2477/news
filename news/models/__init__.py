""":mod:`news.models` --- Abstract News model interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides abstract common news model interfaces that should be implemeted
backends.

"""
from celery import states as celery_states


__all__ = ['AbstractModel', 'AbstractSchedule', 'AbstractNews']


# ===============
# Abstract models
# ===============

class AbstractModel(object):
    """Provides common model interface that should be implemented by
    backends."""

    #: (:class:`int`) Id or primary key of the model.
    id = NotImplementedError


class AbstractSchedule(AbstractModel):
    """Provides schedule meta model interface that should be implemented by
    backends."""

    #: (:class:`str`) Url of the schedule.
    url = NotImplementedError

    #: (:class:`~news.models.abstract.AbstractModel` implementation) Owner of
    #: the schedule.
    owner = NotImplementedError

    #: (:class:`str`) A type of news to fetch. This field is used when mapping
    #: a schedule to a desired reporter class to be used fetching process.
    news_type = NotImplementedError

    #: (:class:`bool`) Schedule activation status.
    enabled = NotImplementedError

    #: (:class:`int`) Schedule's news update cycle in minutes.
    cycle = NotImplementedError

    #: (:class:`dict`) Schedule's options for reporters.
    options = NotImplementedError

    def get_state(self, celery):
        """Returns current celery task state of the schedule.

        :param celery: Celery instance running for news fetch tasks.
        :type celery: :class:`~celery.Celery`

        """
        try:
            return celery.AsyncResult(str(self.id)).state
        except Exception:
            return celery_states.PENDING


class AbstractNews(AbstractModel):
    """
    Provides news model interface that should be implemented by backends.
    It also contains some default implementations for derivative properties.

    """
    @classmethod
    def create_instance(
            cls, url, schedule, title, content, summary,
            published=None, src=None, author=None, image=None):
        """
        Provides common interface to create models and abstracts different
        behaviours of model constructors away from various types of orms.

        :param url: Url of the news.
        :type url: :class:`str`
        :param schedule: Schedule that fetched the news.
        :type schedule: :class:`~news.models.AbstractSchedule` implementation
        :param title: Title of the news.
        :type title: :class:`str`
        :param content: Content of the news.
        :type content: :class:`str`
        :param summary: Summary of the news.
        :type summary: :class:`str`
        :param published: Published datetime of the news.
        :type published: :class:`~datetime.datetime`
        :param src: Parent news of the news.
        :type src: :class:`~news.models.AbstractNews` implementation
        :param author: Name of the news's author
        :type author: :class:`str`
        :param image: URL to the news's image
        :type image: :class:`str`
        :returns: Should return instance of a News fetched by a reporter.
        :rtype: :class:`~news.models.AbstractNews` implementation

        """
        return cls(url=url, schedule=schedule, src=src, author=author,
                   title=title, content=content, summary=summary,
                   image=image, published=published)

    #: (:class:`str`) Url of the news.
    url = NotImplementedError

    #: (:class:`~news.models.abstract.AbstractSchedule` implementation)
    #: Schedule that the news belongs to.
    schedule = NotImplementedError

    #: (:class:`~news.models.abstract.AbstractNews` implementation)
    #: Parent news from which the url of the news has been found.
    src = NotImplementedError

    #: (:class:`str`) Author of the news.
    author = NotImplementedError

    #: (:class:`str`) Title of the news.
    title = NotImplementedError

    #: (:class:`str`) Full content of the news.
    content = NotImplementedError

    #: (:class:`str`) Summary of the news.
    summary = NotImplementedError

    #: (:class:`str`) Image of the news.
    image = NotImplementedError

    #: (:class: `~datetime.datetime`)
    #: Published datetime of the news.
    published = NotImplementedError

    #: (:class: `~datetime.datetime`)
    #: Created datetime of the news.
    created = NotImplementedError

    #: (:class: `~datetime.datetime`)
    #: Updated datetime of the news.
    updated = NotImplementedError

    @property
    def owner(self):
        """(:class:`~news.models.abstract.AbstractModel` implementation) Owner
        of the news."""
        return self.schedule.owner

    @property
    def root(self):
        """(:class:`~news.models.abstract.AbstractNews` implementation) Root
        news of the news."""
        return self if not self.src else self.src.root

    @property
    def is_root(self):
        """(:class:`bool`) Returns `True` if the news is root news."""
        return self.src is None

    @property
    def distance(self):
        """(:class:`int`) Distance from the root news."""
        return 0 if not self.src else self.src.distance + 1


class Readable(AbstractNews):
    """Partial implementation of :class:`AbstractNews`.

    Contains only news content related attributes(e.g. title, content,
    summary, etc.) and leave other instance-level attributes(e.g. src,
    schedule, etc.) as `None`.

    This class is useful when passing parsed news content from
    `~news.reporters.Reporter.parse` to `~news.reporters.Reporter.make_news`
    without fully instantiating news models.

    """
    def __init__(self, title, content, summary,
                 author=None, image=None, published=None):
        # `ReadableItem` doesn't contain any logical information than news
        # content itself.
        self.schedule = None
        self.src = None

        self.author = author
        self.title = title
        self.content = content
        self.summary = summary
        self.image = image

        self.published = published
        self.created = None
        self.updated = None
