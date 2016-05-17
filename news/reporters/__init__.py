import functools
import aiohttp


class ReporterMeta(object):
    """Meta information of a reporter."""
    def __init__(self, schedule):
        self.schedule = schedule

    @property
    def owner(self):
        """(:class:`~news.models.AbstractSchedule` implemntation)Owner of the
        reporter's schedule."""
        return self.schedule.owner

    @property
    def options(self):
        """(:class:`dict`)Reporter options."""
        return self.schedule.options


class Reporter(object):
    """Abstract base class for all reporters."""

    def __init__(self, target, meta, backend,
                 dispatch_middlewares=None,
                 fetch_middlewares=None,
                 *args, **kwargs):
        self.target = target
        self.meta = meta
        self.backend = backend
        self._fetch_middlewares = fetch_middlewares or []
        self._dispatch_middlewares = dispatch_middlewares or []

    @classmethod
    def create_instance(cls, target, meta, backend, *args, **kwargs):
        """Create an reporter.

        :param target: A target to assign to a reporter.
        :type target: :class:`str`
        :param meta: Meta information of a reporter.
        :type meta: :class:`ReporterMeta`
        :param backend: A news backend to be used.
        :type backend: :class:`~news.backends.AbstractBackend` implementation

        :returns: An instance of a `Reporter` implementation.
        :rtype: `Reporter` implementation.

        """
        return cls(target, meta, backend, *args, **kwargs)

    @property
    def schedule(self):
        """(:class:`~news.models.AbstractSchedule` implementation) Schedule of
        the reporter."""
        return self.meta.schedule

    @property
    def owner(self):
        """(:class:`~news.models.AbstractModel` implementation)Owner of the
        reporter."""
        return self.meta.owner

    def report_news(self, *news):
        """Report news to the backend.

        :param *news: News to report to backend of the reporter.
        :type *news: Arbirtrary number of (:class:`~news.models.AbstractNews`)
            implementation.
        """
        self.backend.save_news(*news)

    async def fetch(self):
        """Fetches target of the reporter and returns news.

        :returns: Either a list of news or a news.
        :rtype: :class:`list` or `~news.models.AbstractNews` implemnetation.

        """
        async with aiohttp.get(self.url) as response:
            # return nothing if status code is not OK
            if response.status != 200:
                return None

            # make news from the response
            items = self.parse(await response.text())

            # return a single news if we have only one. return a list of news
            # if we have more than a single news.
            try:
                return (self.make_news(item) for item in items)
            except TypeError:
                item = items
                news = self.make_news(item)
                return news

    async def dispatch(self):
        """Dispatches the reporter to it's target and returns a list of news.

        Should be implemented by all reporter subclasses.  Defaults to rasing
        `NotImplementedError`.

        :returns: A list of news.
        :rtype: :class:`list`

        """
        raise NotImplementedError

    def parse(self, content):
        """Parses fetched response body into a list of items.

        Should be implemented by all reporter subclasses. Defaults to rasing
        `NotImplementedError`.

        :returns: A list of items each to be passed to `make_news` method.
        :rtype: :class:`list`

        """
        raise NotImplementedError

    def make_news(self, item):
        """Make a news instance from the passed item.

        Should be implemented by all reporter subclasses. Defaults to rasing
        `NotImplementedError`.

        :returns: An instance of `~news.models.AbstractNews` implementation.
        :rtype: :class:`~news.models.AbstractNews` implementation.

        """
        raise NotImplementedError

    def enhance(self):
        self.enhance_fetch(self._fetch_middlewares)
        self.enhance_dispatch(self._dispatch_middlewares)
        self._fetch_middlewares = []
        self._dispatch_middlewares = []

    def enhance_dispatch(self, *middlewares):
        self.dispatch = functools.reduce(
            lambda dispatch, middleware: middleware(self, dispatch),
            middlewares, self.dispatch
        )

    def enhance_fetch(self, *middlewares):
        self.fetch = functools.reduce(
            lambda fetch, middleware: middleware(self, fetch), middlewares,
            self.fetch
        )

    def worth_to_report(self, news):
        return True

    def worth_to_visit(self, news, target):
        return True
