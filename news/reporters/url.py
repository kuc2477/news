""":mod:`news.reporters.url` --- URL reporters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide a concrete URL news reporter.

"""
from bs4 import BeautifulSoup
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
    :type meta: :class:`news.reporters.ReporterMeta`
    :param backend: Backend to report news.
    :type backend: :class:`~news.backends.abstract.AbstractBackend`
    :param url: A url to assign to a reporter.
    :type url: :class:`str`
    :param parent: Parent of the reporter. Defaults to `None`.
    :type parent: :class:`TraversingReporter`
    :param request_middlewares: Request middlewares to pipe.
    :type request_middlewares: :class:`list`
    :param response_middlewares: Response middlewares to pipe.
    :type response_middlewares: :class:`list`
    :param loop: Event loop that this reporter will be running on.
    :type loop: :class:`asyncio.BaseEventLoop`
    :param executor: Process pool executor to utilize multiple cores on
        parsing.
    :type executor: :class:`concurrent.futures.ProcessPoolExecutor`
    :param intel: Intels to use for batch traversing.
    :type intel: :class:`list` of news

    """
    parser = 'news.parsers.parse_html'

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
