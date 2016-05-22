import copy
import itertools
import asyncio
from . import Reporter


class TraversingReporter(Reporter):
    """Base class for tree traversing reporters.

    All subclasses of the `TraversingReporter` must implement 'parse()',
    'make_news()' and 'get_urls()'.

    :param parent: Parent of the reporter. Defaults to `None`.
    :type parent: :class:`TraversingReporter`

    """
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._visited_urls_lock = asyncio.Lock()
        self._visited_urls = set()
        self._fetched_news = None
        self.parent = parent

    @property
    def root(self):
        """(:class:`TraversingReporter`)Root reporter."""
        return self if self.is_root else self.parent.root

    @property
    def is_root(self):
        """(:class:`bool`)Returns `True` if the reporter is a root reporter."""
        return self.parent is None

    @property
    def distance(self):
        """(:class:`int`)Returns the distance from the root reporter."""
        return 0 if not self.parent else self.parent.distance + 1

    @property
    def fetched_news(self):
        """(:class:`~news.models.AbstractNews`)Fetched news. Defaults to `None`
        if the reporter hasn't fetched a news yet."""
        return self._fetched_news

    @fetched_news.setter
    def fetched_news(self, news):
        self._fetched_news = news

    async def dispatch(self, bulk_report=True):
        # fetch news from the url and determine whether it is worthy or not
        news = self.fetch()
        if news and not bulk_report:
            self.report_news(news)

        urls = self.get_urls(news) if news else []
        worthy_urls = (t for t in urls if self.worth_to_visit(t))

        news_linked = await self.dispatch_reporters(
            worthy_urls, bulk_report=bulk_report
        )
        news_total = news_linked + [news] if news else news_linked

        # Bulk report news if the flag is set to `True`. We don't have to
        # take care of case of `False` since news should be reported on
        # `dispatch()` calls of each successor reporters already if
        # `bulk_report` flag was given `True`.
        if bulk_report and self.is_chief:
            self.report_news(*set(news_total))

        return news_total

    async def dispatch_reporters(self, urls, *args, **kwargs):
        reporters = self.recruit_reporters(urls)
        if not reporters:
            return []

        dispatches = [r.dispatch(*args, **kwargs) for r in reporters]
        news_sets = await asyncio.gather(*dispatches, return_exceptions=True)
        news_sets_valid = (ns for ns in news_sets if
                           ns and not isinstance(ns, Exception))

        return itertools.chain(*news_sets_valid)

    async def fetch(self):
        news = super().fetch()

        # set fetched and report visit
        self.fetched_news = news
        await self.report_visit()

        if news is None or not self.worth_to_report(news):
            return None
        else:
            return news

    def get_urls(self, news):
        """(:class:`list`)Should return a list of urls to be fetched by
        children of the reporter. Not implemented for default."""
        raise NotImplementedError

    def recruit_reporters(self, urls=None):
        return [self._inherit_meta(t) for t in urls or []]

    async def report_visit(self):
        with (await self._visited_urls_lock()):
            self.root._visited_urls.add(self.url)

    async def already_visited(self, url):
        with (await self._visited_urls_lock()):
            return url in self.root._visited_urls

    async def get_visited(self):
        with (await self._visited_urls_lock()):
            return self.root._visited_urls

    def _inherit_meta(self, url, parent=None):
        # we only inherit fetch middleware. dispatch middleware won't be
        # inherited down to descendents.
        fetch_middlewares = copy.deepcopy(self._fetch_middlewares_applied)

        # we do not inherit intel to children to avoid bunch of
        # useless bulk requests.
        child = self.create(
            meta=self.meta, backend=self.backend, url=url,
            fetch_middlewares=fetch_middlewares
        )
        if isinstance(child, TraversingReporter):
            child.parent = parent
        return child


class FeedReporter(Reporter):
    """Base class for feed reporters."""
    def dispatch(self):
        return (n for n in self.fetch() if self.worth_to_report(n))
