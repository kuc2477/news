""":mod:`news.page` --- Scrapped news and utility functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides page utility functions and :class:`~news.page.Page` class.

"""
from itertools import chain

from cached_property import cached_property
from bs4 import BeautifulSoup
from extraction import Extractor
from asyncio import gather
import aiohttp

from .utils import (
    logger, fillurl, ext, issuburl,
    normalize, depth
)


class News(object):
    """News containing page meta information.

    provides an asynchronous linked news fetching interface.

    :param site: The site of the news.
    :type site: :class:`news.site.Site`
    :param src: The source news of the news.
    :type src: :class:`news.news.News`
    :param url: The url of the news.
    :type url: :class:`str`
    :param content: The content of the news.
    :type content: :class:`str`

    """

    def __init__(self, site, src, url, content):
        self.site = site
        self.src = src
        self.url = normalize(url)
        self.content = content

    def __eq__(self, other):
        return (isinstance(other, News) and
                self.url == other.url and
                self.site.url == other.site.url)

    def __hash__(self):
        return hash(self.url) ^ hash(self.site.url)

    def __str__(self):
        return '<%s> %s' % (self.url, self.title)

    # ============
    # Main methods
    # ============

    async def fetch_linked_news(self, **kwargs):
        """Recursively fetch linked news from the news content.

        :param reached_urls: Set of reached urls before the method call.
        :type reached_urls: :class:`list`
        :return: List of linked `news`s of the news
        :rtype: :class:`list`

        """
        worthy = self.get_worthy_urls(**kwargs)
        unreached = [u for u in worthy if u not in self.site.reached_urls]

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

        # linked news of the page.
        news = {News(self.site, self, u, c) for c, u in contents}

        # linked page sets from the linked news of the page.
        linked_page_sets = await gather(*[page.fetch_linked_news(**kwargs)
                                          for page in news])

        return news.union(set(chain(*linked_page_sets)))

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
    def depth(self):
        return depth(self.site.url, self.url)

    @property
    def distance(self):
        """Returns distance from the root page.

        :return: Distance from the root page.
        :rtype: :class:`int`

        """
        return 0 if self.src is None else self.src.distance + 1

    @cached_property
    def extracted(self):
        extractor = Extractor()
        return extractor.extract(self.content)

    @property
    def title(self):
        return self.extracted.title

    @property
    def image(self):
        return self.extracted.image

    @property
    def description(self):
        return self.extracted.description

    def worth_visit(self, url, maxdepth=None, maxdist=None, brothers=[],
                    blacklist=['png', 'jpg', 'gif', 'pdf', 'svg', 'zip']):
        """Returns boolean value whether the url is worth to explore or not.

        :param url: The url to test if it is worth to visit.
        :type url: :class:`str`
        :param maxdepth: Maximum depth allowed for linked news.
        :type maxdepth: :class:`int` or `None`
        :param maxdist: Maximum distance allowed for linked news.
        :type maxdist: :class:`int` or `None`
        :param blacklist: The extname blacklist for linked news.
        :type blacklist: :class:`list`

        """
        normalized_brothers = [normalize(brother) for brother in brothers]

        is_child = issuburl(self.site.url, url)
        is_relative = any([issuburl(b.url, url) for b in normalized_brothers])
        depth_ok = depth(self.site.url, url) <= maxdepth if \
            maxdepth is not None else True

        distance_ok = self.distance < maxdist if maxdist is not None else True
        blacklist_ok = ext(url) not in blacklist

        return ((is_child and depth_ok) or is_relative) and distance_ok and \
            blacklist_ok

    def get_worthy_urls(self, **kwargs):
        """Returns full urls of linked urls worth to visit from the page.

        :return: Full urls of the anchor tags worth to visit.
        :rtype: :class:`set`

        """
        anchors = BeautifulSoup(self.content, 'html.parser')('a')
        urls = [a['href'] for a in anchors if a.has_attr('href')]

        return {fillurl(self.site.url, u) for u in urls if
                self.worth_visit(u, **kwargs)}

    def to_json(self):
        return {
            'site': self.site.url,
            'src': self.src.url if self.src is not None else None,
            'url': self.url,
            'content': self.content,
            'title': self.title,
            'image': self.image,
            'description': self.description
        }
