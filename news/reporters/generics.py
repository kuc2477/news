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
    :type backend: :class:`news.backends.abstract.AbstractBackend`
    :param url: A url to assign to a reporter.
    :type url: :class:`str`
    :param parent: Parent of the reporter. Defaults to `None`.
    :type parent: :class:`TraversingReporter`
    :param bulk_report: Report news in bulk if given `True`.
    :type bulk_report: :class:`bool`
    :param dispatch_middlewares: Dispatch middlewares to apply.
    :type dispatch_middlewares: :class:`list`
    :param fetch_middlewares: Fetch middlewares to apply.
    :type fetch_middlewares: :class:`list`

    .. note::

        All subclasses of the
        :class:`~news.reporters.generics.TraversingReporter` must implement
        :meth:`parse`, :meth:`make_news` and :meth:`get_urls`.

    """
    def __init__(self, meta, backend, url=None, parent=None, bulk_report=True,
                 dispatch_middlewares=None, fetch_middlewares=None,
                 *args, **kwargs):
        super().__init__(meta=meta, backend=backend, url=url, *args, **kwargs)
        self._visited_urls_lock = asyncio.Lock()
        self._visited_urls = set()
        self._fetched_news = None
        self.parent = parent
        self.bulk_report = bulk_report

    @property
    def root(self):
        """(:class:`TraversingReporter`) Root reporter."""
        return self if self.is_root else self.parent.root

    @property
    def is_root(self):
        """(:class:`bool`) Returns `True` if the reporter is a root reporter."""
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
        if news and not self.bulk_report:
            self.report_news(news)

        urls = await self.get_urls(news) if news else []
        worthies = await asyncio.gather(*[self.worth_to_visit(u) for u in urls])
        worthy_urls = (u for u, w in zip(urls, worthies) if w)

        news_linked = await self.dispatch_reporters(worthy_urls)
        news_total = news_linked + [news] if news else news_linked

        # Bulk report news if the flag is set to `True`. We don't have to
        # take care of case of `False` since news should be reported on
        # `dispatch()` calls of each successor reporters already if
        # `bulk_report` flag was given `True`.
        if self.bulk_report and self.is_root:
            self.report_news(*set(news_total))

        return news_total

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
        news = await super().fetch()

        # set fetched and report visit
        self.fetched_news = news
        await self.report_visit()

        if news is None or not await self.worth_to_report(news):
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
        return [self._inherit_meta(t) for t in urls or []]

    async def report_visit(self):
        """Report to the root reporter that the reporter visited assigned url.
        """
        with (await self._visited_urls_lock):
            self.root._visited_urls.add(self.url)

    async def already_visited(self, url):
        """Check if any descendent of the root reporter has already visited
        the given url.

        :param url: Url to check if we have already visited.
        :type url: :class:`str`
        :returns: `True` if we already visited.
        :rtype: :class:`bool`

        """
        with (await self._visited_urls_lock):
            return url in self.root._visited_urls

    async def get_visited(self):
        """Get all visited urls from the root reporter.

        :returns: All visited urls by the time of calling the method.
        :rtype: :class:`set`

        """
        with (await self._visited_urls_lock):
            return self.root._visited_urls

    def _inherit_meta(self, url, parent=None):
        # we only inherit fetch middleware. dispatch middleware won't be
        # inherited down to descendents.
        fetch_middlewares = copy.deepcopy(self._fetch_middlewares_applied)

        # we do not inherit intel to children to avoid bunch of
        # useless bulk requests.
        child = self.create_instance(
            meta=self.meta, backend=self.backend, url=url,
            fetch_middlewares=fetch_middlewares
        ).enhance()
        if isinstance(child, TraversingReporter):
            child.parent = parent
        return child


class FeedReporter(Reporter):
    """Base class for feed reporters

    :param meta: Reporter meta from which to populate the reporter.
    :type meta: :class:`news.reporters.ReporterMeta`
    :param backend: Backend to report news.
    :type backend: :class:`~news.backends.abstract.AbstractBackend`
    :param url: A url to assign to a reporter.
    :type url: :class:`str`
    :param dispatch_middlewares: Dispatch middlewares to apply.
    :type dispatch_middlewares: :class:`list`
    :param fetch_middlewares: Fetch middlewares to apply.
    :type fetch_middlewares: :class:`list`

    .. note::

        All subclasses of the :class:`FeedReporter` must implement
        :meth:`parse`, :meth:`make_news`.

    """
    async def dispatch(self):
        """Dispatch the reporter to the feed url."""
        fetched = await self.fetch()
        worthies = await asyncio.gather(*[
            self.worth_to_report(n) for n in fetched
        ])
        return (n for n, w in zip(fetched, worthies) if w)
