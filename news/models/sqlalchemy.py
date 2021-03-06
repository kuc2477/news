""":mod:`news.models.sqlalchemy` --- Model SQLAlchemy implementations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides factory functions for both abstract and concrete News models.

"""
import copy
from datetime import datetime
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    String,
    Boolean,
    DateTime,
    event
)
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import (
    relationship,
    backref,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils.types import (
    URLType,
    JSONType,
)
from .abstract import (
    AbstractSchedule,
    AbstractNews
)
from ..constants import (
    DEFAULT_SCHEDULE_CYCLE,
    DEFAULT_SCHEDULE_TYPE,
    DEFAULT_OPTIONS,
)

__all__ = [
    'create_schedule_abc', 'create_news_abc',
    'create_schedule', 'create_news',
    'create_default_schedule', 'create_default_news',
]


def create_schedule_abc(user_model):
    """Abstract base schedule model factory

    :param user_model: User model to use as schedule owners.
    :type user_model: :class:`~news.models.AbstractModel`
        implementation.
    :returns: A abstract base schedule model.
    :rtype: Abstract base sqlalchemy model of
        :class:`~news.models.AbstractSchedule` implementation

    """
    class AbstractBaseSchedule(AbstractSchedule):
        __tablename__ = 'schedule'

        @declared_attr
        def __table_args__(cls):
            return (UniqueConstraint('owner_id', 'url'),)

        @declared_attr
        def owner_id(cls):
            return Column(Integer, ForeignKey(user_model.id))

        @declared_attr
        def owner(cls):
            return relationship(user_model, backref='schedules')

        def __init__(self, owner=None, url='', enabled=False,
                     cycle=DEFAULT_SCHEDULE_CYCLE,
                     type=DEFAULT_SCHEDULE_TYPE, options=None):
            self.owner = owner
            self.url = url
            self.cycle = cycle
            self.enabled = enabled
            self.type = type
            self.options = options or copy.deepcopy(DEFAULT_OPTIONS)

        id = Column(Integer, primary_key=True)
        url = Column(URLType, nullable=False)
        enabled = Column(Boolean, nullable=False, default=False)
        cycle = Column(Integer, default=DEFAULT_SCHEDULE_CYCLE, nullable=False)
        type = Column(
            String, nullable=False,
            default=DEFAULT_SCHEDULE_TYPE
        )
        options = Column(JSONType, nullable=False, default=DEFAULT_OPTIONS)

    return AbstractBaseSchedule


def create_news_abc(schedule_model):
    """
    Abstract base news model factory

    :param schedule_model: Schedule model to use as news's schedule.
    :type schedule_model: Any concrete schedule model of abc models from
        :func:`~create_abc_schedule` factory function.
    :returns: A abstract base news model.
    :rtype: Abstract base sqlalchemy model of
        :class:`~news.models.Abstractnews` implementation

    """
    class AbstractBaseNews(AbstractNews):
        __tablename__ = 'news'

        @declared_attr
        def __table_args__(cls):
            return (UniqueConstraint('schedule_id', 'url'),)

        @declared_attr
        def schedule_id(cls):
            return Column(Integer, ForeignKey('schedule.id'))

        @declared_attr
        def schedule(cls):
            return relationship(
                schedule_model,
                backref=backref(
                    'news_list', cascade='all, delete-orphan',
                    cascade_backrefs=False
                ),
            )

        @declared_attr
        def parent_id(cls):
            return Column(Integer, ForeignKey('news.id'))

        @declared_attr
        def parent(cls):
            return relationship(
                'News',
                remote_side=[cls.id],
                backref=backref(
                    'children', cascade='all, delete-orphan',
                    cascade_backrefs=False
                ),
            )

        @property
        def owner(self):
            return self.schedule.owner

        id = Column(Integer, primary_key=True)
        url = Column(URLType, nullable=False)
        content = Column(Text, nullable=False)
        author = Column(Text, nullable=True)
        title = Column(Text, nullable=False)
        summary = Column(Text, nullable=False)
        image = Column(Text, nullable=True)
        published = Column(DateTime, nullable=True)
        created = Column(DateTime, default=datetime.now)
        updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)

        @classmethod
        def create_instance(cls, url, schedule, title, content, summary,
                            published=None, parent=None, author=None,
                            image=None):
            return cls(url=url, schedule=schedule, parent=parent,
                       author=author, title=title, content=content,
                       summary=summary, image=image, published=published)

        def __init__(self, url='', schedule=None, parent=None, author=None,
                     title=None, content=None, summary=None, image=None,
                     published=None):
            self.url = url
            self.schedule = schedule
            self.parent = parent
            self.author = author
            self.title = title
            self.content = content
            self.summary = summary
            self.image = image
            self.published = published

        def __repr__(self):
            return 'News {} of schedule {}'.format(
                self.url, self.schedule_id
            )

        def __hash__(self):
            return hash(self.__repr__())

        def __eq__(self, other):
            return self.__hash__() == other.__hash__()

    return AbstractBaseNews


def create_schedule(abc_schedule, base, mixins=None, persister=None):
    """Concrete schedule model factory.

    :param abc_schedule: Abstract base schedule to use as base.
    :type abc_schedule: Any ABC schedule from :func:`~create_abc_schedule`
        factory function.
    :param base: SQLAlchemy model base to use.
    :type base: Any SQLAlchemy model base from
        :func:`sqlalchemy.ext.declarative.declarative_base` factory function
    :param mixins: Mixins to be mixed into concrete schedule model.
    :type mixins: Iterable mixin classes.
    :param persister: Persister to use for the schedule persistence.
    :type persister: :class:`~news.persistence.ScheduleNotifier`
    :returns: Concrete schedule model based on given abc schedule.
    :rtype: :class:`~news.models.AbstractSchedule` SQLAlchemy
        implementation based on given abc schedule, model base and mixins.

    """
    mixins = mixins or tuple()
    Schedule = type('Schedule', mixins + (abc_schedule, base), {})

    # connect persister if given
    if persister:
        event.listens_for(Schedule, 'after_insert')(
            lambda mapper, connection, target:
            persister.notify_saved(target, created=True)
        )
        event.listens_for(Schedule, 'after_update')(
            lambda mapper, connection, target:
            persister.notify_saved(target, created=False)
        )
        event.listens_for(Schedule, 'after_delete')(
            lambda mapper, connection, target:
            persister.notify_deleted(target)
        )

    return Schedule


def create_news(abc_news, base, mixins=None):
    """Concrete news model factory.

    :param abc_news: Abstract base news to use as base.
    :type abc_news: Any ABC news from :func:`~create_abc_news` factory
        function.
    :param base: SQLAlchemy model base to use.
    :type base: Any SQLAlchemy model base from
        :func:`sqlalchemy.ext.declarative.declarative_base` factory function
    :param mixins: Mixins to be mixed into concrete news model.
    :type mixins: Iterable mixin classes.
    :returns: Concrete news model based on given abc news and mixins.
    :rtype: :class:`~news.models.AbstractNews` SQLAlchemy
        implementation based on given abc news and model base.

    """
    mixins = mixins or tuple()
    return type('News', mixins + (abc_news, base), {})


def create_default_schedule(user_model, base, persister=None):
    """Default schedule model factory.

    :param user_model: User model to use as schedule owners.
    :type user_model: :class:`~news.models.abstract.AbstractModel`
        implementation
    :returns: A default schedule model.
    :rtype: Default SQLAlchemy :class:`~news.models.AbstractSchedule`
        implementation

    """
    schedule_abc = create_schedule_abc(user_model, base)
    return create_schedule(schedule_abc, base, persister=persister)


def create_default_news(schedule_model, base):
    """Default news model factory.

    :param schedule_model: Schedule model to use as news's schedule.
    :type schedule_model: :class:`~news.models.abstract.AbstractSchedule`
        implementation
    :returns: A abstract base news model.
    :rtype: Default SQLAlchemy :class:`~news.models.Abstractnews`
        implementation

    """
    news_abc = create_news_abc(schedule_model, base)
    return create_news(news_abc, base)
