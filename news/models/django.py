from django.db import models
from django.conf import settings
from jsonfield import JSONField

from . import (
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


__all__ = ['AbstractBaseSchedule', 'AbstractBaseNews', 'Schedule', 'News']


def AbstractBaseSchedule(owner_model=settings.AUTH_USER_MODEL):
    class AbstractBase(models.Model, AbstractSchedule):
        owner = models.ForeignKey(
            settings.AUTH_USER_MODEL, related_name='schedules',
            db_index=True
        )

        url = models.URLField()
        cycle = models.IntegerField(default=DEFAULT_SCHEDULE_CYCLE)

        max_dist = models.IntegerField(
            blank=True, null=True, default=DEFAULT_MAX_DIST)
        max_depth = models.IntegerField(
            blank=True, null=True, default=DEFAULT_MAX_DEPTH)

        blacklist = JSONField(default=DEFAULT_BLACKLIST)
        brothers = JSONField(default=DEFAULT_BROTHERS)

        def get_filter_options(self):
            return {
                'max_dist': self.max_dist,
                'max_depth': self.max_depth,
                'blacklist': self.blacklist,
                'brothers': self.brothers
            }

        class Meta:
            abstract = True
            unique_together = (('owner', 'url'),)

    return AbstractBase


def AbstractBaseNews(schedule_model):
    class AbstractBase(models.Model, AbstractNews):
        schedule = models.ForeignKey(
            schedule_model, related_name='news_list', db_index=True
        )
        src = models.ForeignKey(
            'self', related_name='children', db_index=True,
            blank=True, null=True
        )

        url = models.URLField()
        content = models.TextField()

        @classmethod
        def create_instance(cls, schedule, url, content, src=None):
            return cls(schedule=schedule, url=url, content=content, src=src)

        class Meta:
            abstract = True
            unique_together = (('schedule', 'url'),)

    return AbstractBase


class Schedule(AbstractBaseSchedule()):
    pass


class News(AbstractBaseNews(Schedule)):
    pass
