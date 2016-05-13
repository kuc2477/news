import itertools
import asyncio


class TraversingReporter(AbstractReporter):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._visited_targets_lock = asyncio.Lock()
        self._visited_targets = set()

    @property
    def root(self):
        return self if self.is_root else self.parent.root

    @property
    def is_root(self):
        return self.parent is None

    @property
    def distance(self):
        return 0 if not self.parent else self.parent.distance + 1

    def fetch(self):
        news = super().fetch()
        # TODO: NOT IMPLEMENTED YET

    def dispatch(self, bulk_report=True):
        # fetch news from the url and determine whether it is worthy or not
        news = self.fetch()
        news = news if news and self.worth_to_report(news) else None

        if news and not bulk_report:
            self.report_news(news)

        targets = await self.get_worthy_targets(news) if news else []
        news_linked = await self.dispatch_reporters(urls, bulk_report)
        news_total = news_linked + [news] if news else news_linked

        # Bulk report news if the flag is set to `True`. We don't have to
        # take care of case of `False` since news should be reported on
        # `dispatch()` calls of each successor reporters already if
        # `bulk_report` flag was given `True`.
        if bulk_report and self.is_chief:
            self.report_news(*set(news_total))

        return news_total

    def dispatch_reporters(self, targets, *args, **kwargs):
        reporters = self.recruit_reporters(targets)
        if not reporters:
            return []

        dispatches = [r.dispatch(*args, **kwargs) for r in reporters]
        news_sets = await asyncio.gather(*dispatches, return_exceptions=True)

        return itertools.chain(*[ns for ns in news_sets if
                                 ns and not isinstance(ns, Exception)])

    def get_worthy_targets(self, news):
        raise NotImplementedError

    def recruit_reporters(self, targets):
        return [self._inherit_meta(t) for t in targets]

    async def report_visit(self):
        with (await self._visited_targets_lock()):
            self.root._visited_targets.add(self.target)

    async def already_visited(self, target):
        with (await self._visited_targets_lock()):
            return target in self.root._visited_targets

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


class FeedReporter(AbstractReporter):
    pass
