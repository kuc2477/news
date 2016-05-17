import itertools
import asyncio
from . import Reporter


class TraversingReporter(Reporter):
    """Base class for tree traversing reporters.

    All subclasses of the `TraversingReporter` must implement 'parse()',
    'make_news()' and 'get_targets()'.

    :param parent: Parent of the reporter. Defaults to `None`.
    :type parent: :class:`TraversingReporter`

    """
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._visited_targets_lock = asyncio.Lock()
        self._visited_targets = set()
        self._fetched_news = None

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
        news = news if news and self.worth_to_report(news) else None

        # set news fetched and report that we visited the target
        self.fetched_news = news
        await self.report_visit()

        if news and not bulk_report:
            self.report_news(news)

        targets = self.get_targets(news) if news else []
        worthy_targets = (t for t in targets if self.worth_to_visit(t))

        news_linked = await self.dispatch_reporters(
            worthy_targets, bulk_report=bulk_report
        )
        news_total = news_linked + [news] if news else news_linked

        # Bulk report news if the flag is set to `True`. We don't have to
        # take care of case of `False` since news should be reported on
        # `dispatch()` calls of each successor reporters already if
        # `bulk_report` flag was given `True`.
        if bulk_report and self.is_chief:
            self.report_news(*set(news_total))

        return news_total

    async def dispatch_reporters(self, targets, *args, **kwargs):
        reporters = self.recruit_reporters(targets)
        if not reporters:
            return []

        dispatches = [r.dispatch(*args, **kwargs) for r in reporters]
        news_sets = await asyncio.gather(*dispatches, return_exceptions=True)
        news_sets_valid = (ns for ns in news_sets if
                           ns and not isinstance(ns, Exception))

        return itertools.chain(*news_sets_valid)

    def get_targets(self, news):
        """(:class:`list`)Should return a list of targets to be fetched by
        children of the reporter. Not implemented for default."""
        raise NotImplementedError

    def recruit_reporters(self, targets):
        return [self._inherit_meta(t) for t in targets]

    async def report_visit(self):
        with (await self._visited_targets_lock()):
            self.root._visited_targets.add(self.target)

    async def already_visited(self, target):
        with (await self._visited_targets_lock()):
            return target in self.root._visited_targets

    async def get_visited(self):
        with (await self._visited_targets_lock()):
            return self.root._visited_targets

    def _inherit_meta(self, target, parent=None):
        # we do not inherit intel to children to avoid bunch of
        # useless bulk requests.
        child = self.create(
            target=target, backend=self.backend,
            meta=self.meta
        )
        if isinstance(child, TraversingReporter):
            child.parent = parent
        return child


class FeedReporter(Reporter):
    """Base class for feed reporters."""
    def dispatch(self):
        return (n for n in self.fetch() if self.worth_to_report(n))
