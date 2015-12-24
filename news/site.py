""":mod: `news.site` --- Site to be scrapped and ranked periodically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides site utility functions and :class:`~news.site.Site` class.

"""
from urllib.parse import urlparse

import asyncio
import aiohttp

from .page import Page


class Site(object):
    """"Site to be scrapped, ranked and stored periodically.

    :param url: The url of the site.
    :type url: :class:`str`
    :param ranker: The ranker to use for filter out meaningless pages.
    :type ranker: :class:`news.ranker.BaseRanker`
    :param backend: The backend to use for page storage.
    :type backend: :class:`news.backend.BackendBase`

    """

    def __init__(self, url, backend, ranker,
                 blacklist=['png', 'jpg', 'gif', 'pdf', 'svg']):
        self.url = url
        self.backend = backend
        self.ranker = ranker
        self.blacklist = blacklist

    async def update_pages(self):
        new_pages =  await self.fetch_pages()
        self.backend.add_pages(*new_pages)

    async def fetch_pages(self):
        # Initialize temporary url store for fetching pages.
        self.fetched_urls = []

        """Fetch meaningful pages from the site based on the ranker.

        :return: `page`s of the site.
        :rtype: :class:`list`

        """
        async with aiohttp.get(self.url) as response:
            # Initialize temporary url store to check fetch progress.
            self.fetched_urls = [self.url]

            root = Page(self, self.url, await response.text(), None)
            return [root] + await root.fetch_linked_pages()

    @property
    def urls(self):
        return self.backend.urls

    @property
    def scheme(self):
        return urlparse(self.url).scheme

    @property
    def hostname(self):
        return urlparse(self.url).hostname
