""":mod:`news.page` --- Scrapped pages and utility functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides page utility functions and :class:`~news.page.Page` class.

"""
from urllib.parse import urlparse

from asyncio import gather
import aiohttp

from bs4 import BeautifulSoup


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

    def __init__(self, site, src, url, content):
        self.site = site
        self.src = src
        self.url = url
        self.content = content

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
        urls = [self.build_url(l) for l in self.links if
                self.build_url(l) not in
                self.site.urls + self.site.fetched_urls]

        # Return an empty list if no new urls exist in the page.
        if not urls:
            return []
        # Otherwise accumulate to fetched urls.
        else:
            self.site.fetched_urls += urls

        responses = await gather(*[aiohttp.get(url) for url in urls])
        contents = await gather(*[response.text() for response in responses])
        pages = [Page(self.site, self, url, content) for
                 (url, content) in zip(urls, contents)]


        # Recursively fetch and return linked pages.
        return [linked_page for linked_pages in
                await page.fetch_linked_pages() for page in pages]


    def to_json(self):
        return {
            'site_url': self.site.url,
            'src_url': self.src.url if self.src is not None else None,
            'url': self.url,
            'content': self.content
        }


    # ===============
    # Utility methods
    # ===============

    def build_url(self, url):
        parsed = urlparse(url)
        return '%s://%s%s' % (
            self.site.scheme,
            self.site.hostname,
            parsed.geturl()
        ) if _ispath(url) else parsed.geturl()

    def hassamehost(self, url):
        """Tests if given url is resides in same domain of the page.

        :return: whether given url resides in the same domain or not.
        :rtype: :class:`bool`

        """
        parsed = urlparse(url)
        return _ispath(url) or self.site.hostname == parsed.hostname


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
    def links(self):
        """Returns all linked urls in the page.

        :return: parsed urls of the anchor tags with the same domain.
        :rtype: :class:`list`

        """
        anchors = BeautifulSoup(self.content)('a')
        return [a['href'] for a in anchors if self.hassamehost(a['href'])]


def _ispath(url):
    parsed = urlparse(url)
    return not parsed.scheme and not parsed.hostname
