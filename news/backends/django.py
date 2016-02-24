""":mod:`news.backends.django` --- Django backend. """
from django.db import transaction
from django.db.models.signals import (
    post_save,
    post_delete
)
from . import AbstractBackend


class DjangoBackend(AbstractBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.OwnerManager = self.owner_class.objects
        self.ScheduleManager = self.schedule_class.objects
        self.NewsManager = self.news_class.objects

    def get_news(self, owner, url):
        return self.ScheduleManager\
            .filter(schedule__owner=owner)\
            .filter(url=url)\
            .first()

    def get_news_list(self, owner, root_url):
        return self.ScheduleManager\
            .filter(url=root_url)\
            .filter(owner=owner)\
            .all()

    @transaction.atomic
    def save_news(self, *news):
        for n in news:
            if not self.news_exists(n.owner, n.url):
                self.cascade_save_news(n)
            else:
                previous = self.get_news(n.owner, n.url)
                previous.content = n.content
                previous.src = n.src
                previous.save()

    @transaction.atomic
    def cascade_save_news(self, news):
        if news.src and news.src.id is None:
            self.cascade_save_news(news.src)
        news.save()

    def delete_news(self, *news):
        queryset = self.NewsManager.filter(id__in=[n.id for n in news])
        queryset.delete()

    def get_schedule(self, owner, url):
        return self.ScheduleManager\
            .filter(owner=owner)\
            .filter(url=url)\
            .first()

    def get_schedules(self, owner=None, url=None):
        queryset = self.ScheduleManager.all()

        if owner:
            queryset = queryset.filter(owner=owner)
        if url:
            queryset = queryset.filter(url=url)

        return queryset.all()

    def set_schedule_save_listener(self, listener):
        post_save.connect(listener, sender=self.schedule_class, weak=False)

    def set_schedule_delete_listener(self, listener):
        post_delete.connect(listener, sender=self.schedule_class, weak=False)
