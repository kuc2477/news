""":mod:`news.cover` --- News cover
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

News cover jobs to be run by reporters.

"""
import asyncio
from .reporters import ReporterMeta
from concurrent.futures import ProcessPoolExecutor


class Cover(object):
    """News cover that can be run by :class:`news.scheduler.Scheduler`'s
    celery task.

    :param schedule: Schedule that dispatches this cover.
    :type schedule: `backend`'s'
        :attr:`~news.backend.abstract.AbstractBackend.Schedule`
    :param backend: Backend to be used for news cover.
    :type backend: :class:`~news.backends.abstract.AbstractBackend`
        implementation.

    """
    def __init__(self, schedule, backend):
        self.schedule = schedule
        self.backend = backend
        self.reporter = None
        self.loop = None

    def prepare(self, reporter_class,
                dispatch_middlewares=None,
                fetch_middlewares=None, **kwargs):
        """Prepare a reporter for the cover.

        :param reporter_class: Reporter class to use.
        :type reporter_class: :class:`~news.reporters.Reporter`
        :param dispatch_middlewares: Dispatch middlewares to enhance the
            reporter's `dispatch` method.
        :type dispatch_middlewares: :class:`list` of functions that takes
            an reporter and it's dispatch method as arguments and returns
            enhanced `dispatch` method.
        :param fetch_middlewares: Fetch middlewares to enhance the reporter's
            `fetch` method.
        :type fetch_middlewares: :class:`list` of functions that takes an
            reporter and it's fetch method as arguments and returns enhanced
            `fetch` method.
        :returns: Prepared cover itself.
        :rtype: `~news.cover.Cover`

        """
        meta = ReporterMeta(self.schedule)
        backend = self.backend

        # set event loop and executor for the reporter
        self.loop = asyncio.get_event_loop()
        self.executor = ProcessPoolExecutor()

        # set root reporter of the cover.
        self.reporter = reporter_class.create_instance(
            meta=meta, backend=backend,
            dispatch_middlewares=dispatch_middlewares,
            fetch_middlewares=fetch_middlewares,
            loop=self.loop, executor=self.executor,
            **kwargs
        ).enhance()

        return self

    def run(self, **dispatch_options):
        """Run the news cover.

        Since the cover will be run on `asnycio`'s base event loop, this
        method should be called in another background worker to avoid blocking.

        :param **dispatch_options: Optional dispatch options that will be feed
            to the reporter's `dispatch` method call.
        :type **dispatch_options: :class:`dict`
        :returns: A list of news.
        :rtype: :class:`list`

        """
        # prepare the reporter with bare experience and middlewares if he is
        # not ready to be dispatched yet.
        assert(self.reporter and self.loop), 'Cover is not prepared yet'
        return self.loop.run_until_complete(
            self.reporter.dispatch(**dispatch_options)
        )
