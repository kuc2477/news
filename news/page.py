""":mod:`news.page` --- Scrapped pages and utility functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides page utility functions and :class:`~news.page.Page` class.

"""
import os.path
import logging

from itertools import chain
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from asyncio import gather
import aiohttp

from .utils import logger
from .utils import fillurl, ext, issuburl


class Page(object):
    """Scrapped page containing various page meta information.

    Abstracts a scrapped page and provides an asynchronous page fetching
    interface.

    :param site: The site of the page.
    :type site: :class:`news.site.Site`
    :param src: The source page of the page.
    :type src: :class:`news.page.Page`
    :param url: The url of the page.
    :type url: :class:`str`
    :param content: The content of the page.
    :type content: :class:`str`

    """

    def __init__(self, site, url, content, src):
        self.site = site
        self.url = url
        self.content = content
        self.src = src

    def __eq__(self, other):
        return isinstance(other, Page) and self.url == other.url


    # ============
    # Main methods
    # ============

    async def fetch_linked_pages(self):
        """Recursively fetch linked pages from the page.

        :return: `page`s of the site.
        :rtype: :class:`list`

        """

        # gather only valid responses
        valid_response_urls = []
        valid_responses = []
        for url in self.unreached_urls:
            try :
                response = await aiohttp.get(url)
            except Exception:
                logger.warning('{} invalid response!' % url)
                continue
            else:
                logger.info('{}: valid response!' % url)
                valid_response_urls.append(url)
                valid_responses.append(response)

        # gather only valid contents
        valid_content_urls = []
        valid_contents = []
        for url, response in zip(valid_response_urls, valid_responses):
            try:
                content = await response.text()
            except UnicodeError:
                logger.warning('{}: invalid content!' % url)
                continue
            else:
                logger.info('{}: valid content!' % url)
                valid_content_urls.append(url)
                valid_contents.append(content)

        # Initialize temporary url store if not initialized yet and acuumulate
        # fetched urls.
        self.site.fetched_urls = getattr(self.site, 'fetched_urls', [])
        self.site.fetched_urls += valid_content_urls

        # pages of the page
        pages = [Page(self.site, url, content, self) for
                 url, content in zip(valid_content_urls, valid_contents)]

        # linked pages of the pages from the page
        linked_page_sets = await gather(*[
            page.fetch_linked_pages() for page in pages
        ])

        return pages + list(chain(*linked_page_sets))

    def to_json(self):
        return {
            'site': self.site.url,
            'src': self.src.url if self.src is not None else None,
            'url': self.url,
            'content': self.content
        }


    # ==========
    # Properties
    # ==========

    @property
    def root(self):
        """Returns root page of the page.

        :return: Root page of the page.
        :rtype: :class:`news.page.Page`

        """
        return self if self.src is None else self.src.root

    @property
    def urls(self):
        """Returns full urls of valid linked urls in the page.

        :return: full urls of the anchor tags in the same domain.
        :rtype: :class:`set`

        """
        anchors = BeautifulSoup(self.content, 'html.parser')('a')

        return {fillurl(self.site.url, a['href']) for a in anchors if
                is_anchor_valid_for_site(self.site, a)}

    @property
    def unreached_urls(self):
        return [url for url in self.urls if url not in
                self.site.urls + getattr(self.site, 'fetched_urls', [])]


def is_anchor_valid_for_site(site, a):
    return a.has_attr('href') and issuburl(site.url, a['href']) and \
        ext(a['href']) not in site.blacklist
