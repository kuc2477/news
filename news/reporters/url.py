""":mod:`news.reporters.url` --- URL reporters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide a concrete URL news reporter.

"""
from bs4 import BeautifulSoup
from extraction import Extractor
from ..models.abstract import Readable
from .generics import TraversingReporter
from .mixins import (
    BatchTraversingMixin,
    DomainTraversingMixin
)
from ..utils.url import fillurl


class URLReporter(
        BatchTraversingMixin,
        DomainTraversingMixin,
        TraversingReporter):
    """URL Reporter for fetching news from plain html web pages.

    :param meta: Reporter meta from which to populate the reporter.
    :type meta: :class:`~news.reporters.ReporterMeta`
    :param backend: Backend to report news.
    :type backend: :class:`~news.backends.abstract.AbstractBackend`
        implementation
    :param intel: Intels to use for batch traversing.
    :type intel: :class:`list` of news

    """
    def parse(self, content):
        """Parses html content of http response body into a single
        :class:`~news.models.abstract.Readable`.

        Internally uses :class:`~extraction.Extractor` extractor to extract
        sementic tags from the plain html content.

        :param content: Http response body
        :type content: :class:`str`
        :returns: A parsed readable
        :rtype: :class:`~news.models.abstract.Readable`

        """
        extractor = Extractor()
        extracted = extractor.extract(content)
        return Readable(url=self.url, title=extracted.title, content=content,
                        summary=extracted.description, image=extracted.image)

    def make_news(self, readable):
        """Instantiate a news out of the readable parsed from :meth:`parse`.

        :param readable: A parsed readable.
        :type readable: :class:`~news.models.abstract.Readable`
        :returns: A news instance
        :rtype: :class:`~news.models.abstract.AbstractNews` implementation

        """
        parent = self.parent.fetched_news if not self.is_root else None
        stored = self.backend.get_news_by(owner=self.owner, url=self.url)
        fetched = self.fetched_news

        if not fetched and not stored:
            news = self.backend.News.create_instance(
                parent=parent, schedule=self.schedule,
                **readable.kwargs()
            )
        else:
            news = fetched or stored
            news.parent = parent
            for k, v in readable.kwargs().items():
                setattr(news, k, v)

        return news

    async def get_urls(self, news):
        """Retrieve urls to visit from the instantiated news.

        :param news: Instantiated news from the :meth:`make_news`
        :type news: :class:`~news.models.abstract.AbstractNews` implementation
        :returns: A set of urls retrieved from the response body.
        :rtype: :set:

        """
        atags = BeautifulSoup(news.content, 'html.parser')('a')
        links = {a['href'] for a in atags if a.has_attr('href')}
        return {fillurl(self.root.url, l) for l in links}
