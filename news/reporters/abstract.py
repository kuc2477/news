""":mod:`news.reporters.abstract` --- Abstract reporter base classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide abstract base classes for reporters.

"""
import copy
import functools
import aiohttp


class Reporter(object):
    """Abstract base class for all reporters."""

    def __init__(self, meta, backend, url=None,
                 dispatch_middlewares=None,
                 fetch_middlewares=None, **kwargs):
        self.url = url or meta.schedule.url
        self.meta = meta
        self.backend = backend

        self._fetch_middlewares = fetch_middlewares or []
        self._fetch_middlewares_applied = []
        self._dispatch_middlewares = dispatch_middlewares or []
        self._dispatch_middlewares_applied= []

    @classmethod
    def create_instance(
            cls, meta, backend, url=None,
            dispatch_middlewares=None,
            fetch_middlewares=None, **kwargs):
        """Create an reporter.

        :param url: A url to assign to a reporter.
        :type url: :class:`str`
        :param meta: Meta information of a reporter.
        :type meta: :class:`ReporterMeta`
        :param backend: A news backend to be used.
        :type backend: :class:`~news.backends.AbstractBackend` implementation
        :param dispatch_middlewares: Dispatch middlewares to apply.
        :type dispatch_middlewares: :class:`list`
        :param fetch_middlewares: Fetch middlewares to apply.
        :type fetch_middlewares: :class:`list`

        :returns: An instance of a `Reporter` implementation.
        :rtype: `Reporter` implementation.

        """
        return cls(meta=meta, backend=backend, url=url,
                   dispatch_middlewares=dispatch_middlewares,
                   fetch_middlewares=fetch_middlewares, **kwargs)

    @property
    def schedule(self):
        """(:class:`~news.models.AbstractSchedule` implementation) Schedule of
        the reporter."""
        return self.meta.schedule

    @property
    def options(self):
        """(:class:`dict`) Reporter options."""
        return self.schedule.options

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
        """Fetches url of the reporter and returns news.

        :returns: Either a list of news or a news.
        :rtype: :class:`list` or `~news.models.AbstractNews` implemnetation.

        """
        print('original fetch')
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
        """Dispatches the reporter to it's url and returns a list of news.

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
        """Enhance the reporter with it's middlewares.

        Note that middlewares will be exhausted after the enhancement, leaving 
        an empty lists.

        :returns: Ehanced reporter itself.
        :rtype: :class:`~news.reporters.Reporter`

        """
        self.enhance_fetch(*self._fetch_middlewares)
        self.enhance_dispatch(*self._dispatch_middlewares)
        self._fetch_middlewares = []
        self._dispatch_middlewares = []
        return self

    def enhance_dispatch(self, *middlewares):
        """Enhance the reporter's `dispatch()` method with middlewares.

        :param *middlewares: An arbitrary number of dispatch method enhancers.
        :type *middlewares: A function that takes a reporter and dispatch
            method as arguments and returns enhanced dispatch method.
        :returns: Enhanced reporter itself.
        :rtype: :class:`~news.reporters.Reporter`

        """
        for middleware in middlewares:
            self.dispatch = middleware(self, self.dispatch)
            self._dispatch_middlewares_applied.append(middleware)
        return self

    def enhance_fetch(self, *middlewares):
        """Enhance the reporter's `fetch()` method with middlewares.

        :param *middlewares: An arbitrary number of fetch method enhancers.
        :type *middlewares: A function that takes a reporter and fetch method
            as arguments and returns enhanced fetch method.

        """
        for middleware in middlewares:
            self.fetch = middleware(self, self.fetch)
            self._fetch_middlewares_applied.append(middleware)
        return self

    async def worth_to_report(self, news):
        """Decides whether the reporter should report the news to it's backend
        or not. The default implementation always returns `True`.

        :param news: A news to test it's worthiness.
        :type news: :class:`~news.models.AbstractNews` implementation.
        :returns: `True` if the news is expected to be worthy to report.
        :rtype: :class:`bool`

        """
        return True

    async def worth_to_visit(self, news, url):
        """Decides whether the reporter should visit the link of the news.
        The default implementation always returns `True`.

        :param news: A news that contains the link.
        :type news: :class:`~news.models.AbstractNews` implementation.
        :param url: A URL to test it's worthiness.
        :type url: :class:`str`
        :returns: `True` if the url of the news is expected to be worthy to
        visit.
        :rtype: :class:`bool`

        """
        return True
