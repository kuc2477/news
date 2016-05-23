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

from .import (
    AbstractSchedule,
    AbstractNews
)
from ..constants import (
    DEFAULT_SCHEDULE_CYCLE,
    DEFAULT_SCHEDULE_NEWS_TYPE,
    NEWS_TYPE_MAX_LENGTH,
    AUTHOR_MAX_LENGTH,
    TITLE_MAX_LENGTH,
)


__all__ = ['create_abc_schedule', 'create_abc_news',
           'create_schedule', 'create_news']


def create_abc_schedule(user_model=None):
    """Abstract base schedule model factory.

    :param user_model: User model to use as schedule owners.
    :type user_model: :class:`~news.models.AbstractModel`
        implemenatation
    :returns: A abstract base schedule model.
    :rtype: Abstract base django model of
        :class:`~news.models.AbstractSchedule` implementation.

    """
    user_model = user_model or settings.AUTH_USER_MODEL

    class AbstractBaseSchedule(models.Model, AbstractSchedule):
        owner = models.ForeignKey(
            user_model, related_name='schedules', db_index=True)

        url = models.URLField()
        cycle = models.IntegerField(default=DEFAULT_SCHEDULE_CYCLE)
        enabled = models.BooleanField(default=False)
        news_type = models.CharField(max_length=NEWS_TYPE_MAX_LENGTH,
                                     default=DEFAULT_SCHEDULE_NEWS_TYPE)
        options = JSONField(default={})

        class Meta:
            abstract = True
            unique_together = (('owner', 'url'),)

    return AbstractBaseSchedule


def create_abc_news(schedule_model):
    """Abstract base news model factory.

    :param schedule_model: Schedule model to use as news's schedule.
    :type schedule_model: Any concrete schedule model of abc models from
        :func:`~create_abc_schedule` factory function.
    :returns: A abstract base news model.
    :rtype: Abstract base django model of
        :class:`~news.models.AbstractNews` implementation

    """
    class AbstractBaseNews(models.Model, AbstractNews):
        schedule = models.ForeignKey(
            schedule_model, related_name='news_list',
            db_index=True
        )

        parent = models.ForeignKey(
            'self', related_name='children',
            db_index=True, blank=True, null=True
        )

        url = models.URLField()
        author = models.CharField(max_length=AUTHOR_MAX_LENGTH, null=True)
        title = models.CharField(max_length=TITLE_MAX_LENGTH)
        summary = models.TextField()
        content = models.TextField()
        image = models.URLField(null=True)
        published = models.DateTimeField(blank=True, null=True)
        created = models.DateTimeField(auto_now_add=True)
        updated = models.DateTimeField(auto_now=True)

        class Meta:
            abstract = True
            unique_together = (('schedule', 'url'),)
    return AbstractBaseNews


def create_schedule(abc_schedule, mixins=None, persister=None):
    """Concrete schedule model factory.

    :param abc_schedule: Abstract base schedule to use as base.
    :type abc_schedule: Any ABC schedule from :func:`~create_abc_schedule`
        factory function.
    :param mixins: Mixins to be mixed into concrete schedule model.
    :type mixins: Iterable mixin classes.
    :param persister: Persister to use for the schedule persistence.
    :type persister: :class:`~news.persistence.SchedulePersister`
    :returns: Concrete schedule model based on given abc schedule.
    :rtype: :class:`~news.models.AbstractSchedule` Django
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
            persister.notify_saved,
            sender=Schedule, weak=False
        )
        post_delete.connect(
            persister.notify_deleted,
            sender=Schedule, weak=False
        )

    return Schedule


def create_news(abc_news, mixins=None):
    """Concrete news model factory.

    :param abc_news: Abstract base news to use as base.
    :type abc_news: Any ABC news from :func:`~create_abc_news` factory
        function.
    :param mixins: Mixins to be mixed into concrete news model.
    :type mixins: Iterable mixin classes.
    :returns: Concrete news model based on given abc news and mixins.
    :rtype: :class:`~news.models.AbstractNews` Django implementation
        based on given abc news and mixins.

    """
    mixins = mixins or tuple()
    return type(
        'News', mixins + (abc_news,),
        {'__module__': __name__}
    )
