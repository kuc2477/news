import asyncio
from .reporter import (
    ReporterMeta,
    Reporter
)


class Cover(object):
    def __init__(self, backend, schedule, reporter_meta):
        self.backend = backend
        self.schedule = schedule
        self.reporter_meta = reporter_meta
        self.reporter = None

    @classmethod
    def from_schedule(cls, schedule, backend, intel_strategy=None,
                      report_experience=None, fetch_experience=None,
                      dispatch_middlewares=None, fetch_middlewares=None):
        intel_strategy = intel_strategy or (lambda backend: [])
        intel = intel_strategy(backend)

        reporter_meta = ReporterMeta(
            schedule, intel,
            report_experience, fetch_experience,
            dispatch_middlewares, fetch_middlewares
        )
        return cls(backend, schedule, reporter_meta)

    def prepare(self):
        self.reporter = Reporter(
            self.schedule.url,
            self.backend,
            meta=self.reporter_meta
        )

    def run(self, bulk_report=True):
        if not self.reporter:
            self.prepare()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._reporter.dispatch(bulk_report))
