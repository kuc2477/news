""":mod:`news.backends.django` --- Django ORM backend

Django ORM page store backend for news.

"""
import django
from django.conf import settings

from . import BackendBase
from ..page import Page
from ..site import Site
from ..models.django import Page as PageModel
from ..exceptions import InvalidStoreSchemaError


class DjangoBackend(BackendBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def add_pages(self, *pages):
        PageModel.objects.bulk_create([_to_model(page) for page in pages])

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
            return _from_model(self, PageModel.objects.get(url=url))
        except PageModel.DoesNotExist:
            return None

    def get_pages(self, site=None):
        # Site should be either url itself or `~news.site.Site` instance.
        assert(isinstance(site, (str, Site)) or site is None)
        ps = PageModel.objects.all()

        if site is not None:
            ps = ps.filter(site__url=(
                site.url if isinstance(site, Site) else site))

        return [_from_model(self, p) for p in ps]


def _from_model(backend, p):
    return Page(
        Site(p.site, backend),
        p.url, p.content, getattr(p.src, 'url', None)
    )

def _to_model(page):
    return PageModel(
        url=page.url, site=page.site.url,
        src=getattr(page.src, 'url', None),
        content=page.content
    )
