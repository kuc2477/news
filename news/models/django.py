""":mod:`news.models.django` --- News model Django implementations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides factory functions and default News models.

"""
from django.db import models
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


__all__ = ['Schedule', 'News', 'create_abc_schedule', 'create_abc_news']


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


class Schedule(create_abc_schedule()):
    """
    Schedule model default django implementation.

    :param owner: Owner of the schedule.
    :type owner: :class:`~django.contrib.auth.models.User`
    :param url: Url to subscribe.
    :type url: :class:`str`
    :param cycle: News update cycle in minutes.
    :type cycle: :class:`int`
    :param max_dist: Maximum distance to allow for reporters to discover news.
        Defaults to `None`.
    :type max_dist: :class:`int`
    :param max_depth: Maximum depth to allow for reporters to discover news.
        Defaults to `None`.
    :type max_depth: :class:`int`
    :param blacklist: Filetype blacklist for reporters to avoid visiting.
        Carefully designed blacklist might improve performance of your
        reporters.
    :type blacklist: :class:`list`
    :param brothers: Brother urls to allow for reporters to visit even if it
        dosen't match other conditions(e.g. not in same domain).
    :type brothers: :class:`list`

    """


class News(create_abc_news(Schedule)):
    """
    News model default django implementation.

    :param schedule: Schedule which news belongs to.
    :type schedule: :class:`~news.models.django.Schedule`
    :param src: Parent news from which the url of the news has been found.
    :type src: :class:`~news.models.django.News`
    :param url: Url of the news.
    :type url: :class:`str`
    :param content: Content of the news.
    :type content: :class:`str`

    """
