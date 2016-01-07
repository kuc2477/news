import pytest

from news.backends.django import DjangoBackend

from fixtures import *


@pytest.mark.django_db
def test_add_site(django_backend, site):
    assert(not django_backend.site_exists(site))
    django_backend.add_site(site)
    assert(django_backend.site_exists(site))

@pytest.mark.django_db
def test_delete_site(django_backend, site):
    django_backend.add_site(site)
    assert(django_backend.site_exists(site))
    django_backend.delete_site(site)
    assert(not django_backend.site_exists(site))

@pytest.mark.django_db
def test_get_site(django_backend, site):
    django_backend.add_site(site)
    assert(django_backend.get_site(site.url) == site)

@pytest.mark.django_db
def test_add_pages(django_backend, page):
    assert(not django_backend.page_exists(page))
    django_backend.add_pages(page)
    assert(django_backend.page_exists(page))

@pytest.mark.django_db
def test_delete_pages(django_backend, page):
    django_backend.add_pages(page)
    assert(django_backend.page_exists(page))
    django_backend.delete_pages(page)
    assert(not django_backend.page_exists(page))

@pytest.mark.django_db
def test_page_exists(django_backend, page):
    assert(not django_backend.page_exists(page))
    django_backend.add_pages(page)
    assert(django_backend.page_exists(page))
    django_backend.delete_pages(page)
    assert(not django_backend.page_exists(page))

@pytest.mark.django_db
def test_get_page(django_backend, page):
    django_backend.add_pages(page)
    assert(page == django_backend.get_page(page.url))

@pytest.mark.django_db
def test_get_pages(django_backend, page):
    django_backend.add_pages(page)
    assert(page in django_backend.get_pages())

@pytest.mark.django_db
def test_get_urls(django_backend, page):
    django_backend.add_pages(page)
    assert(page.url in django_backend.get_urls())
    assert(len(django_backend.get_urls()) == 1)
