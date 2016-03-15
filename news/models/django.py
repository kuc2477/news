""":mod:`news.models.django` --- News model Django implementations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides factory functions and default News models.

"""
from django.db import models
from django.db.models.signals import (
    post_save,
    post_delete
)
from django.conf import settings
from jsonfield import JSONField

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


def create_abc_schedule(user_model=None):
    """
    Abstract base schedule model factory.

    :param user_model: User model to use as schedule owners.
    :type user_model: :class:`~news.models.abstract.AbstractModel`
        implemenatation
    :returns: A abstract base schedule model.
    :rtype: Abstract base django model of
        :class:`~news.models.abstract.AbstractSchedule` implementation.

    """
    user_model = user_model or settings.AUTH_USER_MODEL

    class AbstractBaseSchedule(models.Model, AbstractSchedule):
        owner = models.ForeignKey(
            user_model, related_name='schedules', db_index=True)

        url = models.URLField()
        cycle = models.IntegerField(default=DEFAULT_SCHEDULE_CYCLE)

        max_dist = models.IntegerField(
            blank=True, null=True, default=DEFAULT_MAX_DIST)
        max_depth = models.IntegerField(
            blank=True, null=True, default=DEFAULT_MAX_DEPTH)
        blacklist = JSONField(default=DEFAULT_BLACKLIST)
        brothers = JSONField(default=DEFAULT_BROTHERS)

        class Meta:
            abstract = True
            unique_together = (('owner', 'url'),)
    return AbstractBaseSchedule


def create_abc_news(schedule_model):
    """
    Abstract base news model factory.

    :param schedule_model: Schedule model to use as news's schedule.
    :type schedule_model: Any concrete schedule model of abc models from
        :func:`~create_abc_schedule` factory function.
    :returns: A abstract base news model.
    :rtype: Abstract base django model of
        :class:`~news.models.abstract.AbstractNews` implementation

    """
    class AbstractBaseNews(models.Model, AbstractNews):
        schedule = models.ForeignKey(schedule_model, related_name='news_list',
                                     db_index=True)
        src = models.ForeignKey('self', related_name='children',
                                db_index=True, blank=True, null=True)

        url = models.URLField()
        content = models.TextField()

        @classmethod
        def create_instance(cls, schedule, url, content, src=None):
            return cls(schedule=schedule, url=url, content=content, src=src)

        class Meta:
            abstract = True
            unique_together = (('schedule', 'url'),)
    return AbstractBaseNews


def create_schedule(abc_schedule, mixins=None, persister=None):
    """
    Concrete schedule model factory.

    :param abc_schedule: Abstract base schedule to use as base.
    :type abc_schedule: Any ABC schedule from :func:`~create_abc_schedule`
        factory function.
    :param mixins: Mixins to be mixed into concrete schedule model.
    :type mixins: Iterable mixin classes.
    :param persister: Persister to use for the schedule persistence.
    :type persister: :class:`~news.persistence.SchedulePersister`
    :returns: Concrete schedule model based on given abc schedule.
    :rtype: :class:`~news.models.abstract.AbstractSchedule` Django
        implementation based on given abc schedule and mixins.

    """
    mixins = mixins or tuple()
    Schedule = type(
        'Schedule', mixins + (abc_schedule,),
        {'__module__': __name__}
    )

    # connect persister if given
    if persister:
        post_save.connect(
            persister.notify_schedule_saved,
            sender=Schedule, weak=False
        )
        post_delete.connect(
            persister.notify_schedule_deleted,
            sender=Schedule, weak=False
        )

    return Schedule


def create_news(abc_news, mixins=None):
    """
    Concrete news model factory.

    :param abc_news: Abstract base news to use as base.
    :type abc_news: Any ABC news from :func:`~create_abc_news` factory
        function.
    :param mixins: Mixins to be mixed into concrete news model.
    :type mixins: Iterable mixin classes.
    :returns: Concrete news model based on given abc news and mixins.
    :rtype: :class:`~news.models.abstract.AbstractNews` Django implementation
        based on given abc news and mixins.

    """
    mixins = mixins or tuple()
    return type(
        'News', mixins + (abc_news,),
        {'__module__': __name__}
    )
