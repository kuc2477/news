from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import (
    declarative_base,
    declared_attr
)
from sqlalchemy_utils.types.url import (
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


__all__ = ['Schedule', 'News', 'create_abc_schedule', 'create_abc_news']


def create_abc_schedule(user_model):
    """Abstract base schedule model factory"""
    class AbstractBaseSchedule(object):
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
            return relationship(user_model, back_populates='schedules')

        id = Column(Integer, primary_key=True)
        url = Column(URLType, nullable=False)
        cycle = Column(Integer, default=DEFAULT_SCHEDULE_CYCLE, nullable=False)
        max_dist = Column(Integer)
        max_depth = Column(Integer)
        blacklist = Column(JSONType, default=DEFAULT_BLACKLIST, nullable=False)
        brothers = Column(JSONType, default=DEFAULT_BROTHERS, nullable=False)

    return AbstractBaseSchedule


def create_abc_news(schedule_model):
    """Abstract base news model factory"""
    class AbstractBaseNews(object):
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
            return relationship(Schedule, back_populates='news_list')

        @declared_attr
        def src_id(cls):
            return Column(Integer, ForeignKey('news.id'))

        @declared_attr
        def src(cls):
            return relationship('News', back_populates='children',
                                remote_side=[id])

        id = Column(Integer, primary_key=True)
        url = Column(URLType, nullable=False)
        content = Column(Text, nullable=False)

        def __init__(self, schedule=None, url='', content='', src=None):
            self.schedule = schedule
            self.url = url
            self.content = content
            self.src = src

        @classmethod
        def create_instance(cls, schedule, url, content, src=None):
            return cls(schedule=schedule, url=url, content=content, src=src)
    return AbstractBaseNews


def create_schedule(abc_schedule, base):
    return type('Schedule', (base, abc_schedule), {})


def create_news(abc_news, base):
    return type('News', (base, abc_news), {})
