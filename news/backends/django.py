""":mod:`news.backends.django` --- Backend Django implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides an implemenation of news backend for django ORM.

"""
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .abstract import AbstractBackend


class DjangoBackend(AbstractBackend):
    def get_news(self, id):
        try:
            return self.News.objects.get(id=id)
        except ObjectDoesNotExist:
            return None

    def get_news_by(self, owner, url):
        return self.News.objects\
            .filter(schedule__owner=owner)\
            .filter(url=url)\
            .first()

    def get_news_list(self, owner=None, root_url=None):
        news_list = self.News.objects.all()

        if owner:
            news_list = news_list.filter(schedule__owner=owner)
        if root_url:
            news_list = news_list.filter(schedule__url=root_url)

        return news_list

    @transaction.atomic
    def save_news(self, *news):
        for n in news:
            if not self.news_exists(n.id):
                self.cascade_save_news(n)
            else:
                previous = self.get_news(n.id)
                previous.content = n.content
                previous.parent = n.parent
                previous.save()

    @transaction.atomic
    def cascade_save_news(self, news):
        if news.parent and news.parent.is_root:
            self.cascade_save_news(news.parent)
        news.save()

    def delete_news(self, *news):
        queryset = self.News.objects.filter(id__in=[n.id for n in news])
        queryset.delete()

    def get_schedule(self, id):
        return self.Schedule.objects.get(id=id)

    def get_schedules(self, owner=None, url=None):
        queryset = self.Schedule.objects.all()

        if owner:
            queryset = queryset.filter(owner=owner)
        if url:
            queryset = queryset.filter(url=url)

        return queryset.all()
