""":mod: `news.site` --- Site to be scrapped and ranked periodically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides site utility functions and :class:`~news.site.Site` class.

"""
from urllib.parse import urlparse

import asyncio
import aiohttp

from .utils import logger
from .utils import normalize
from .page import Page


class Site(object):
    """"Site to be scrapped stored periodically.

    :param url: The url of the site.
    :type url: :class:`str`

    """

    def __init__(self, url, brothers=[]):
        self.url = normalize(url)
        self.brothers = brothers

    def __eq__(self, other):
        return self.url == other.url

    async def fetch_pages(self, **kwargs):
        """Fetch new pages from the site.

        :return: `page`s of the site.
        :rtype: :class:`list`

        """
        async with aiohttp.get(self.url) as response:
            # Initialize url set to check if links has been fetched or not.
            self.reached_urls= {self.url}
            root = Page(self, None, self.url, await response.text())
            return {root}.union(await root.fetch_linked_pages(**kwargs))

    @property
    def scheme(self):
        return urlparse(self.url).scheme

    @property
    def hostname(self):
        return urlparse(self.url).hostname
