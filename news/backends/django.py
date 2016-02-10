""":mod:`news.backends.django` --- Django ORM backend

Django ORM news store backend for news.

"""
from . import BackendBase
from ..news import News
from ..site import Site
from ..models.django import (
    News as NewsModel,
    Site as SiteModel
)


class DjangoBackend(BackendBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def add_news(self, *news):
        # add site if the site of news doesn't exist in the store
        for site in {n.site for n in news if not self.site_exists(n.site)}:
            self.add_site(site)

        NewsModel.objects.bulk_create([
            _model_from_news(n) for n in news])

    def update_news(self, *news):
        # TODO: NOT IMPLEMENTED YET
        pass

    def delete_news(self, *news):
        NewsModel.objects.filter(url__in=[n.url for n in news]).delete()

    def news_exists(self, news):
        # News should be either url itself or `~news.news.News` instance.
        assert(isinstance(news, (str, News)))
        return NewsModel.objects.filter(
            url=(news.url if isinstance(news, News) else news)
        ).exists()

    def get_news(self, url):
        try:
            return _news_from_model(NewsModel.objects.get(url=url))
        except NewsModel.DoesNotExist:
            return None

    def get_news_list(self, site=None):
        # Site should be either url itself or `~news.site.Site` instance.
        assert(isinstance(site, (str, Site)) or site is None)
        ps = NewsModel.objects.all()

        if site is not None:
            ps = ps.filter(site__url=(
                site.url if isinstance(site, Site) else site))

        return [_news_from_model(p) for p in ps]


def _news_from_model(p):
    return News(
        Site(p.site.url), getattr(p.src, 'url', None),
        p.url, p.content
    )


def _model_from_news(news):
    try:
        site = SiteModel.objects.get(pk=news.site.url)
    except SiteModel.DoesNotExist:
        site = None

    return NewsModel(
        url=news.url, site=site,
        src=getattr(news.src, 'url', None),
        content=news.content
    )
