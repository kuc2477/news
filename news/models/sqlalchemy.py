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
from sqlalchemy.orm import (
    relationship,
    backref
)
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
    """Abstract base schedule model factory"""
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

        id = Column(Integer, primary_key=True)
        url = Column(URLType, nullable=False)
        cycle = Column(Integer, default=DEFAULT_SCHEDULE_CYCLE, nullable=False)
        max_dist = Column(Integer, default=DEFAULT_MAX_DIST)
        max_depth = Column(Integer, default=DEFAULT_MAX_DEPTH)
        blacklist = Column(JSONType, default=DEFAULT_BLACKLIST, nullable=False)
        brothers = Column(JSONType, default=DEFAULT_BROTHERS, nullable=False)

    return AbstractBaseSchedule


def create_abc_news(schedule_model):
    """Abstract base news model factory"""
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
    return type('Schedule', (abc_schedule, base), {})


def create_news(abc_news, base):
    return type('News', (abc_news, base), {})
