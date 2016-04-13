""":mod:`news.cover` --- News cover jobs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

News cover jobs that will be run by reporters.

"""
import asyncio
from .reporter import (
    ReporterMeta,
    Reporter
)


class Cover(object):
    """
    News cover that can be run asynchronously by
    :class:`news.scheduler.Scheduler`'s celery task.

    :param backend: News backend to be used for news cover.
    :type backend: :class:`~news.backends.AbstractBackend`
        implementation.
    :param schedule: Schedule that this cover is in charge of.
    :type schedule: Backend's
        :attr:`~news.backend.AbstractBackend.schedule_class`

    """
    def __init__(self, backend, schedule):
        self.backend = backend
        self.schedule = schedule
        self.reporter = None
        self.loop = None

    @classmethod
    def from_schedule(cls, schedule, backend):
        """
        Factory method that instantiates cover from the schedule.

        :param schedule: The schedule of which the cover is in charge of.
        :type schedule: :class:`~news.models.AbstractSchedule`
            implementation.
        :param backend: The news backend to use for the cover.
        :type backend: :class:`~news.backends.AbstractBackend`
            implementation.
        :returns: Cover job of the schedule.
        :rtype: :class:`~news.cover.Cover`
        """
        return cls(backend, schedule)

    def prepare(self, intel=None,
                report_experience=None, fetch_experience=None,
                dispatch_middlewares=None, fetch_middlewares=None):
        """
        Prepare a reporter with experience and middlewares for the cover.

        :param intel: News intel that will be used to boost performance of the
            cover. News in the intel list will be fetched in parallel.
        :type intel: :class:`list`
        :param report_experience: Module qualified path to the report
            experience function. The report experience function should take a
            schedule of the news and the news as it's arguments  and return
            `True` if the news is valuable.  Otherwise it should return
            `False`.
        :type report_experience: :class:`str`
        :param fetch_experience: Module qualified path to the fetch experience
            function. The fetch experience function should take a schedule of
            the news, the news and the url to be classified whether it is
            worth to visit or not. The function should return `True` if the
            url is expected to be worthy. Otherwise it should return `False`.
        :type fetch_experience: :class:`str`

        """
        reporter_url = self.schedule.url
        reporter_backend = self.backend
        reporter_meta = ReporterMeta(
            self.schedule, intel=intel,
            report_experience=report_experience,
            fetch_experience=fetch_experience
        )

        # set chief reporter of the cover.
        self.reporter = Reporter(
            reporter_url,
            reporter_meta,
            reporter_backend,
        )

        # apply middlewares on the reporter if exists.
        for middleware in (dispatch_middlewares or []):
            self.reporter.enhance_dispatch(middleware)

        for middleware in (fetch_middlewares or []):
            self.reporter.enhance_fetch(middleware)

        # set event loop for the reporter
        self.loop = asyncio.get_event_loop()

    def run(self, bulk_report=True):
        """
        Run the news cover. News that has been fetched for the first time will
        be created in backend as :class:`~news.models.AbstractNews`
        implemenattion's instance. News that already exists will be updated.

        Since the cover will be run in `asnycio`'s base event loop, this
        method should be called in another background worker.

        :param bulK_report: News will be reported in bulk if given True. This
            can be used to avoid backend save overload on each saves of the
            news.
        :type bulK_report: :class:`bool`

        """
        # prepare the reporter with bare experience and middlewares if he is
        # not ready to be dispatched yet.
        if not self.reporter or not self.loop:
            self.prepare()

        return self.loop.run_until_complete(
            self.reporter.dispatch(bulk_report)
        )
