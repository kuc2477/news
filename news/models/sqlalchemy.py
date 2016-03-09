""":mod:`news.models.sqlalchemy` --- News model SQLAlchemy implementations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides factory functions for both abstract and concrete News models.

"""
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text
)
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils.types import (
    URLType,
    JSONType
)
from .abstract import (
    AbstractSchedule,
    AbstractNews
)
from ..constants import (
    DEFAULT_SCHEDULE_CYCLE,
    DEFAULT_MAX_DIST,
    DEFAULT_MAX_DEPTH,
    DEFAULT_BLACKLIST,
    DEFAULT_BROTHERS
)


__all__ = ['create_abc_schedule', 'create_abc_news',
           'create_schedule', 'create_news']


def create_abc_schedule(user_model):
    """
    Abstract base schedule model factory

    :param user_model: User model to use as schedule owners.
    :type user_model: :class:`~news.models.abstract.AbstractModel`
        implementation.
    :returns: A abstract base schedule model.
    :rtype: Abstract base sqlalchemy model of
        :class:`~news.models.abstract.AbstractSchedule` implementation

    """
    class AbstractBaseSchedule(AbstractSchedule):
        @declared_attr
        def __tablename__(cls):
            return 'schedule'

        @declared_attr
        def __table_args__(cls):
            return (UniqueConstraint('owner_id', 'url'),)

        @declared_attr
        def owner_id(cls):
            return Column(Integer, ForeignKey(user_model.id))

        @declared_attr
        def owner(cls):
            return relationship(user_model, backref='schedules')

        def __init__(self, url='', cycle=DEFAULT_SCHEDULE_CYCLE,
                     max_dist=DEFAULT_MAX_DIST, max_depth=DEFAULT_MAX_DEPTH,
                     blacklist=DEFAULT_BLACKLIST, brothers=DEFAULT_BROTHERS):
            self.url = url
            self.cycle = cycle
            self.max_dist = max_dist
            self.max_depth = max_depth
            self.blacklist = blacklist
            self.brothers = brothers

        id = Column(Integer, primary_key=True)
        url = Column(URLType, nullable=False)
        cycle = Column(Integer, default=DEFAULT_SCHEDULE_CYCLE, nullable=False)
        max_dist = Column(Integer, default=DEFAULT_MAX_DIST)
        max_depth = Column(Integer, default=DEFAULT_MAX_DEPTH)
        blacklist = Column(JSONType, default=DEFAULT_BLACKLIST, nullable=False)
        brothers = Column(JSONType, default=DEFAULT_BROTHERS, nullable=False)

    return AbstractBaseSchedule


def create_abc_news(schedule_model):
    """
    Abstract base news model factory

    :param schedule_model: Schedule model to use as news's schedule.
    :type schedule_model: Any concrete schedule model of abc models from
        :func:`~create_abc_schedule` factory function.
    :returns: A abstract base news model.
    :rtype: Abstract base sqlalchemy model of
        :class:`~news.models.abstract.Abstractnews` implementation

    """
    class AbstractBaseNews(AbstractNews):
        @declared_attr
        def __tablename__(cls):
            return 'news'

        @declared_attr
        def __table_args__(cls):
            return (UniqueConstraint('schedule_id', 'url'),)

        @declared_attr
        def schedule_id(cls):
            return Column(Integer, ForeignKey('schedule.id'))

        @declared_attr
        def schedule(cls):
            return relationship(schedule_model, backref='news_list')

        @declared_attr
        def src_id(cls):
            return Column(Integer, ForeignKey('news.id'))

        @declared_attr
        def src(cls):
            return relationship(
                'News', backref='children',
                remote_side=[cls.id]
            )

        id = Column(Integer, primary_key=True)
        url = Column(URLType, nullable=False)
        content = Column(Text, nullable=False)

        def __init__(self, schedule=None, url='', content='', src=None):
            # avoid save-update cascade
            self._schedule = schedule
            self.schedule_id = schedule and schedule.id

            self.url = url
            self.content = content
            self.src = src

        @classmethod
        def create_instance(cls, schedule, url, content, src=None):
            return cls(schedule=schedule, url=url, content=content, src=src)

        @property
        def owner(self):
            return self._schedule and self._schedule.owner

    return AbstractBaseNews


def create_schedule(abc_schedule, base):
    """
    Concrete schedule model factory.

    :param abc_schedule: Abstract base schedule to use as base.
    :type abc_schedule: Any ABC schedule from :func:`~create_abc_schedule`
        factory function.
    :param base: SQLAlchemy model base to use.
    :type base: Any SQLAlchemy model base from
        :func:`sqlalchemy.ext.declarative.declarative_base` factory function
    :returns: Concrete schedule model based on given abc schedule.
    :rtype: :class:`~news.models.abstract.AbstractSchedule` SQLAlchemy
        implementation based on given abc schedule and model base.

    """
    return type('Schedule', (abc_schedule, base), {})


def create_news(abc_news, base):
    """
    Concrete news model factory.

    :param abc_news: Abstract base news to use as base.
    :type abc_news: Any ABC news from :func:`~create_abc_news` factory
        function.
    :param base: SQLAlchemy model base to use.
    :type base: Any SQLAlchemy model base from
        :func:`sqlalchemy.ext.declarative.declarative_base` factory function
    :returns: Concrete news model based on given abc news.
    :rtype: :class:`~news.models.abstract.AbstractNews` SQLAlchemy
        implementation based on given abc news and model base.

    """
    return type('News', (abc_news, base), {})
