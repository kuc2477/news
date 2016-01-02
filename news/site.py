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
    :param backend: The backend to use for page storage.
    :type backend: :class:`news.backend.BackendBase`
    :param brothers: The urls that pages under them also will be considered as
        an subpage of the site.
    :type brothers: :class:`list`
    :param blacklist: The blacklist file extensions to avoid fetching.
    :type blacklist: :class:`list`

    """

    def __init__(self, url, backend, brothers=[],
                 blacklist=['png', 'jpg', 'gif', 'pdf', 'svg']):
        self.url = normalize(url)
        self.backend = backend
        self.brothers = brothers
        self.blacklist = blacklist

    def __eq__(self, other):
        return self.url == other.url

    async def update_pages(self, *callbacks):
        # logging
        logger.debug('%s: News update start' % self.url)

        fetched = await self.fetch_pages()
        new = [p for p in fetched if not self.backend.page_exists(p)]

        # fire callbacks
        if callbacks and new:
            for callback in callbacks:
                callback(new)

        # add new pages
        self.backend.add_pages(*new)

        # notify that we have updated pages for the site.
        logger.debug(
            '%d pages fetched / %d pages updated' %
            (len(fetched), len(new))
        )

    async def fetch_pages(self):
        """Fetch new pages from the site.

        :return: `page`s of the site.
        :rtype: :class:`list`

        """
        async with aiohttp.get(self.url) as response:
            # Initialize url set to check if links has been fetched or not.
            self.reached_urls= {self.url}

            root = Page(self, self.url, await response.text(), None)
            return {root}.union(await root.fetch_linked_pages())


    @property
    def urls(self):
        return self.backend.get_urls(self)

    @property
    def scheme(self):
        return urlparse(self.url).scheme

    @property
    def hostname(self):
        return urlparse(self.url).hostname
