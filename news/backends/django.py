""":mod:`news.backends.django` --- News backend Django implementations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides an implemenation of news backend for django projects.

"""
from django.db import transaction
from .import AbstractBackend


class DjangoBackend(AbstractBackend):
    def get_news(self, owner, url):
        return self.NewsManager\
            .filter(schedule__owner=owner)\
            .filter(url=url)\
            .first()

    def get_news_list(self, owner=None, root_url=None):
        news_list = self.NewsManager.all()

        if owner:
            news_list = news_list.filter(schedule__owner=owner)
        if root_url:
            news_list = news_list.filter(schedule__url=root_url)

        return news_list

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
        if news.src and news.src.is_root:
            self.cascade_save_news(news.src)
        news.save()

    def delete_news(self, *news):
        queryset = self.NewsManager.filter(id__in=[n.id for n in news])
        queryset.delete()

    def get_schedule_by_id(self, id):
        return self.ScheduleManager.get(id=id)

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
