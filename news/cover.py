import asyncio
from .reporter import (
    ReporterMeta,
    Reporter
)


class Cover(object):
    def __init__(self, backend, schedule):
        self.backend = backend
        self.schedule = schedule
        self.reporter = None

    @classmethod
    def from_schedule(cls, schedule, backend):
        return cls(backend, schedule)

    def prepare(self, intel=None,
                report_experience=None, fetch_experience=None,
                dispatch_middlewares=None, fetch_middlewares=None):
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
        if dispatch_middlewares:
            self.reporter.enhance_dispatch(*dispatch_middlewares)
        if fetch_middlewares:
            self.reporter.enhance_fetch(*fetch_middlewares)

    def run(self, bulk_report=True):
        # prepare the reporter with bare experience and middlewares if he is
        # not ready to be dispatched yet.
        if not self.reporter:
            self.prepare()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.reporter.dispatch(bulk_report))
