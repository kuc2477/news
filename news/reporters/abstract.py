""":mod:`news.reporters.abstract` --- Abstract reporter base classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide abstract base classes for reporters.

"""
import functools
import aiohttp
from ..utils.python import importpath


class Reporter(object):
    """Abstract base class for all reporters."""

    #: (:class:`str) Module qualified path to the parser function to use.
    parser = NotImplemented

    def __init__(self, meta, backend, url=None,
                 request_middlewares=None,
                 response_middlewares=None,
                 loop=None, executor=None, **kwargs):
        self.url = url or meta.schedule.url
        self.meta = meta
        self.backend = backend
        self.parse = functools.partial(importpath(self.parser), self.url)

        self.request_middlewares = request_middlewares or []
        self.response_middlewares = response_middlewares or []

        self._loop = loop
        self._executor = executor
        self._client_session = aiohttp.ClientSession(loop=loop)

    @classmethod
    def create_instance(
            cls, meta, backend, url=None,
            request_middlewares=None,
            response_middlewares=None,
            loop=None, executor=None, **kwargs):
        """Create an reporter.

        :param url: A url to assign to a reporter.
        :type url: :class:`str`
        :param meta: Meta information of a reporter.
        :type meta: :class:`ReporterMeta`
        :param backend: Backend to report news.
        :type backend: :class:`~news.backends.abstract.AbstractBackend`
        :param request_middlewares: Request middlewares to pipe.
        :type request_middlewares: :class:`list`
        :param response_middlewares: Response middlewares to pipe.
        :type response_middlewares: :class:`list`
        :param loop: Event loop that this reporter will be running on.
        :type loop: :class:`asyncio.BaseEventLoop`
        :param executor: Process pool executor to utilize multiple cores on
            parsing.
        :type executor: :class:`concurrent.futures.ProcessPoolExecutor`

        :returns: An instance of a `Reporter` implementation.
        :rtype: `Reporter` implementation.

        """
        return cls(meta=meta, backend=backend, url=url,
                   request_middlewares=request_middlewares,
                   response_middlewares=response_middlewares,
                   loop=loop, executor=executor, **kwargs)

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

    async def dispatch(self):
        """Dispatches the reporter to it's url and returns a list of news.

        Should be implemented by all reporter subclasses.  Defaults to rasing
        `NotImplementedError`.

        :returns: A list of news.
        :rtype: :class:`list`

        """
        raise NotImplementedError

    async def fetch(self):
        """Fetches url of the reporter and returns news.

        :returns: Either a list of news or a news.
        :rtype: :class:`list` or `~news.models.AbstractNews` implemnetation.

        """
        # pipe request middlewares
        for middleware in self.request_middlewares:
            self._client_session = await middleware(self, self._client_session)
            if not self._client_session:
                return None

        async with self._client_session.get(self.url) as response:
            # pipe response middlewares
            for middleware in self.response_middlewares:
                response = await middleware(self, response)
                if not response:
                    return None

            # return nothing if status code is not OK
            if response.status != 200:
                return None

            # make news from the response
            readables = await self._loop.run_in_executor(
                self._executor, self.parse, await response.text()
            )

            # return a single news if we have only one. return a list of news
            # if we have more than a single news.
            try:
                return (self.make_news(r) for r in readables if r.valid)
            except TypeError:
                r = readables
                return self.make_news(r) if r.valid else None

    def make_news(self, readable):
        pass

    async def filter_news(self, *news):
        """Decides whether the reporter should report the news to it's backend
        or not. The default implementation just returns passed news.

        :param news: Arbitrary number of news to test it's worthinesses.
        :type news: :class:`~news.models.AbstractNews` implementations.
        :returns: An iterator of filtered news.
        :rtype: iterator

        """
        return news

    async def filter_urls(self, news, *urls):
        """Decides whether the reporter should visit the link of the news.
        The default implementation just returns passed urls.

        :param news: A news that contains the urls.
        :type news: :class:`~news.models.AbstractNews` implementation.
        :param urls: Arbitrary number of urls to test it's worthinesses.
        :type urls: :class:`str`
        :returns: An iterator of filtered urls.
        :rtype: iterator

        """
        return urls
