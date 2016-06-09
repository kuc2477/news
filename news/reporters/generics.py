""":mod:`news.reporters.generics` --- Generic reporters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide generic reporters.

"""
import copy
import itertools
import asyncio
from .abstract import Reporter


class TraversingReporter(Reporter):
    """Base class for tree traversing reporters.

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

    .. note::

        All subclasses of the
        :class:`~news.reporters.generics.TraversingReporter` must implement
        :meth:`make_news` and :meth:`get_urls`.

    """
    def __init__(self, meta, backend, url=None, parent=None,
                 request_middlewares=None, response_middlewares=None,
                 *args, **kwargs):
        super().__init__(
            meta=meta, url=url, backend=backend,
            request_middlewares=request_middlewares,
            response_middlewares=response_middlewares,
            *args, **kwargs
        )
        self._visited_urls_lock = asyncio.Lock()
        self._visited_urls = set()
        self._fetched_news = None
        self.parent = parent

    @property
    def root(self):
        """(:class:`TraversingReporter`) Root reporter."""
        return self if self.is_root else self.parent.root

    @property
    def is_root(self):
        """(:class:`bool`) Returns `True` if the reporter is a root reporter.
        """
        return self.parent is None

    @property
    def distance(self):
        """(:class:`int`) Returns the distance from the root reporter."""
        return 0 if not self.parent else self.parent.distance + 1

    @property
    def fetched_news(self):
        """(:class:`~news.models.abstract.AbstractNews`) Fetched news.
            Defaults to `None` if the reporter hasn't fetched a news yet."""
        return self._fetched_news

    @fetched_news.setter
    def fetched_news(self, news):
        self._fetched_news = news

    async def dispatch(self):
        """Dispatch the traversing reporter and it's descendents.

        :returns: A list of news fetched by the reporter and it's descendents.
        :rtype: :class:`list`

        """
        # fetch news from the url and determine whether it is worthy or not
        news = await self.fetch()

        if not news:
            return []

        urls = await self.get_urls(news)
        worthies = await self.filter_urls(news, *urls)

        news_linked = await self.dispatch_reporters(worthies)
        news_total = itertools.chain(news_linked, [news]) \
            if news else news_linked

        return list(news_total)

    async def dispatch_reporters(self, urls, *args, **kwargs):
        """Dispatch the reporter's descendents to the given urls.

        :returns: A list of news fetched by the descendents.
        :rtype: :class:`list`

        """
        reporters = self.recruit_reporters(urls)
        if not reporters:
            return []

        dispatches = [r.dispatch(*args, **kwargs) for r in reporters]
        news_sets = await asyncio.gather(*dispatches, return_exceptions=True)
        news_sets_valid = (ns for ns in news_sets if
                           ns and not isinstance(ns, Exception))

        return itertools.chain(*news_sets_valid)

    async def fetch(self):
        """Fetch the given url and make an news from it.

        :class:`~news.reporters.generics.TraversingReporter` will carry
        :attr:`fetched_news` and report to it's root reporter that he has
        visited the url after when the fetch has been finished. Theses visited
        urls can later be accessed by :meth:`get_visited` or utilized by
        :meth:`already_visited`.

        :returns: A fetched news
        :rtype: :class:`~news.models.abstract.AbstractNews` implementation

        """
        await self.report_visit()
        self.fetched_news = news = await super().fetch()

        if not news or not await self.filter_news(news):
            return None
        else:
            return news

    async def get_urls(self, news):
        """Should return a list of urls to be fetched by the reporter's
        children.

        :param news: The reporter's fetched news
        :type news: :class:`~news.models.abstract.AbstractNews` implementation.

        .. note:: Not implemented by default.

        """
        raise NotImplementedError

    def recruit_reporters(self, urls=None):
        """Recruit reporters for the given urls.

        :param urls: Urls for which to recruit reporters.
        :type urls: :class:`list`
        :returns: A list of reporters for the given urls.
        :rtype: :class:`list`

        """
        return [self._inherit_meta(t, parent=self) for t in urls or []]

    async def report_visit(self):
        """Report to the root reporter that the reporter visited assigned url.
        """
        with (await self.root._visited_urls_lock):
            self.root._visited_urls.add(self.url)

    async def already_visited(self, url):
        """Check if any descendent of the root reporter has already visited
        the given url.

        :param url: Url to check if we have already visited.
        :type url: :class:`str`
        :returns: `True` if we already visited.
        :rtype: :class:`bool`

        """
        with (await self.root._visited_urls_lock):
            return url in self.root._visited_urls

    async def get_visited(self):
        """Get all visited urls from the root reporter.

        :returns: All visited urls by the time of calling the method.
        :rtype: :class:`set`

        """
        with (await self.root._visited_urls_lock):
            return self.root._visited_urls

    def _inherit_meta(self, url, parent=None):
        request_middlewares = copy.deepcopy(self.request_middlewares)
        response_middlewares = copy.deepcopy(self.response_middlewares)
        return self.create_instance(
            meta=self.meta, backend=self.backend,
            url=url, parent=parent,
            request_middlewares=request_middlewares,
            response_middlewares=response_middlewares,
            loop=self._loop, executor=self._executor,
        )


class FeedReporter(Reporter):
    """Base class for feed reporters

    :param meta: Reporter meta from which to populate the reporter.
    :type meta: :class:`news.reporters.ReporterMeta`
    :param url: A url to assign to a reporter.
    :type url: :class:`str`
    :param request_middlewares: Request middlewares to pipe.
    :type request_middlewares: :class:`list`
    :param response_middlewares: Response middlewares to pipe.
    :type response_middlewares: :class:`list`
    :param loop: Event loop that this reporter will be running on.
    :type loop: :class:`asyncio.BaseEventLoop`
    :param executor: Process pool executor to utilize multiple cores on
    parsing.
    :type executor: :class:`concurrent.futures.ProcessPoolExecutor`

    .. note::

        All subclasses of the :class:`FeedReporter` must implement
        :meth:`make_news`.

    """
    async def dispatch(self):
        """Dispatch the reporter to the feed url."""
        fetched = await self.fetch()
        return await self.filter_news(*fetched)
