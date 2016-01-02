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
from .utils import fillurl, ext, issuburl, normalize


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
        self.url = normalize(url)
        self.content = content
        self.src = src

    def __eq__(self, other):
        return (isinstance(other, Page) and
                self.url == other.url and
                self.site.url == other.site.url)

    def __hash__(self):
        return hash(self.url) ^ hash(self.site.url)


    # ============
    # Main methods
    # ============

    async def fetch_linked_pages(self):
        """Recursively fetch linked pages from the page.

        :param reached_urls: Set of reached urls before the method call.
        :type reached_urls: :class:`list`
        :return: List of linked `page`s of the page
        :rtype: :class:`list`

        """
        unreached = [u for u in self.urls if u not in self.site.reached_urls]

        # update reached urls
        self.site.reached_urls = self.site.reached_urls.union(set(unreached))

        # logging
        for u in unreached:
            logger.warning('[REQUEST] %s' % u)

        responses = [(r, u) for r, u in zip(await gather(
            *[aiohttp.get(u) for u in unreached],
            return_exceptions=True), unreached
        ) if not isinstance(r, Exception)]

        contents = [(c, u) for c, u in zip(await gather(
            *[r.text() for r, u in responses],
            return_exceptions=True), [u for r, u in responses]
        ) if not isinstance(c, Exception)]

        # logging
        for u in [u for c, u in contents]:
            logger.info('[RESPONSE] %s responded with valid contents' % u)
        for u in [u for u in unreached if u not in [u for c, u in contents]]:
            logger.error('[INVALID] %s responded with invalid contents' % u)

        # linked pages of the page.
        pages = {Page(self.site, u, c, self) for c, u in contents}

        # linked page sets from the linked pages.
        linked_page_sets = await gather(*[
            page.fetch_linked_pages() for page in pages
       ])

        return pages.union(set(chain(*linked_page_sets)))

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

        return {normalize(fillurl(self.site.url, a['href']))
                for a in anchors if is_anchor_valid(self.site, a)}


def is_anchor_valid(site, a):
    return (
        a.has_attr('href') and
        any(
            [issuburl(site.url, a['href'])] +
            [issuburl(u, a['href']) for u in site.brothers]
        ) and ext(a['href']) not in site.blacklist
    )
