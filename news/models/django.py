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


def create_abc_schedule(user_model=settings.AUTH_USER_MODEL):
    """Abstract base schedule model factory"""
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
    """Abstract base news model factory"""
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
    """Default schedule model"""


class News(create_abc_news(Schedule)):
    """Default news model"""
