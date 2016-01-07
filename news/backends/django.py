""":mod:`news.backends.django` --- Django ORM backend

Django ORM page store backend for news.

"""
import django
from django.conf import settings

from . import BackendBase
from ..page import Page
from ..site import Site
from ..models.django import (
    Page as PageModel,
    Site as SiteModel
)
from ..exceptions import InvalidStoreSchemaError


class DjangoBackend(BackendBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def add_site(self, site):
        SiteModel.objects.create(url=site.url)

    def delete_site(self, site):
        try :
            SiteModel.objects.get(pk=site.url).delete()
        except SiteModel.DoesNotExist:
            pass

    def get_site(self, url):
        return Site(url) if SiteModel.objects.filter(pk=url).exists() else None

    def add_pages(self, *pages):
        # add site if the site of page doesn't exist in the store
        for site in {page.site for page in pages if not self.site_exists(page.site)}:
            self.add_site(site)

        PageModel.objects.bulk_create([_model_from_page(page) for page in pages])

    def delete_pages(self, *pages):
        PageModel.objects.filter(url__in=[page.url for page in pages]).delete()

    def page_exists(self, page):
        # Page should be either url itself or `~news.page.Page` instance.
        assert(isinstance(page, (str, Page)))
        return PageModel.objects.filter(
            url=(page.url if isinstance(page, Page) else page)
        ).exists()

    def get_page(self, url):
        try:
            return _page_from_model(PageModel.objects.get(url=url))
        except PageModel.DoesNotExist:
            return None

    def get_pages(self, site=None):
        # Site should be either url itself or `~news.site.Site` instance.
        assert(isinstance(site, (str, Site)) or site is None)
        ps = PageModel.objects.all()

        if site is not None:
            ps = ps.filter(site__url=(
                site.url if isinstance(site, Site) else site))

        return [_page_from_model(p) for p in ps]


def _page_from_model(p):
    return Page(Site(p.site.url), getattr(p.src, 'url', None), p.url, p.content)

def _model_from_page(page):
    try:
        site = SiteModel.objects.get(pk=page.site.url)
    except SiteModel.DoesNotExist:
        site = None

    return PageModel(
        url=page.url, site=site,
        src=getattr(page.src, 'url', None),
        content=page.content
    )
