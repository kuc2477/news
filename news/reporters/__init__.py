import aiohttp


class ReporterMeta(object):
    def __init__(self, schedule):
        self.schedule = schedule

    @property
    def owner(self):
        return self.schedule.owner

    @property
    def options(self):
        return self.schedule.options


class AbstractReporter(object):
    def __init__(self, target, meta, backend,
                 dispatch_middlewares=None,
                 fetch_middlewares=None,
                 *args, **kwargs):
        self.target = target
        self.meta = meta
        self.backend = backend
        self._fetch_middlewares = fetch_middlewares or []
        self._dispatch_middlewares = dispatch_middlewares or []
        self._fetched_news = None

    @classmethod
    def create(cls, target, meta, backend, *args, **kwargs):
        return cls(target, meta, backend, *args, **kwargs)

    @property
    def fetched_news(self):
        return self._fetched_news

    @fetched_news.setter
    def fetched_news(self, news):
        self._fetched_news = news

    @property
    def schedule(self):
        return self.meta.schedule

    @property
    def owner(self):
        return self.meta.owner

    def report_news(self, *news):
        self.backend.save_news(*news)

    async def fetch(self):
        async with aiohttp.get(self.url) as response:
            # return nothing if status code is not OK
            if response.status != 200:
                return None

            # make news from response
            return self.make_news(await response.text())

    async def dispatch(self, bulk_report=True):
        raise NotImplementedError

    def make_news(self, content):
        raise NotImplementedError

    def enhance_dispatch(self, *middlewares):
        raise NotImplementedError

    def enhance_fetch(self, *middlewares):
        raise NotImplementedError

    def worth_to_report(self, news):
        return True

    def worth_to_visit(self, news, target):
        return True
