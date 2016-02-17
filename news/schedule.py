""":mod: `news.schedule` --- Schedule related domain classes.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Provides schedule related domain classes which will be usually used by other
processes or threads in background.

"""
import asyncio
import schedule as worker

from .reporter import (
    Reporter,
    ReporterMeta
)
from .constants import (
    DEFAULT_SCHEDULE_CYCLE,
    DEFAULT_FILTER_OPTIONS
)


class Schedule(object):
    def __init__(self, backend, schedule_meta, reporter_meta):
        self.backend = backend
        self.schedule_meta = schedule_meta
        self.reporter_meta = reporter_meta
        self.reporter = None

    @classmethod
    def from_meta(cls, schedule_meta, backend, intel_strategy=None,
                  report_experience=None, fetch_experience=None,
                  dispatch_middlewares=None, fetch_middlewares=None):
        intel_strategy = intel_strategy or (lambda backend: [])
        intel = intel_strategy(backend)

        reporter_meta = ReporterMeta(
            intel,
            report_experience, fetch_experience,
            dispatch_middlewares, fetch_middlewares,
            **schedule_meta.get_filter_options()
        )
        return cls(backend, schedule_meta, reporter_meta)

    def prepare(self):
        self._reporter = Reporter(
            self._backend,
            self._schedule_meta.get_url,
            meta=self._reporter_meta
        )

    def run(self, bulk_report=True):
        if not self._reporter:
            self.prepare()
        return self._reporter.dispatch(bulk_report)


class Scheduler(object):
    def __init__(self, backend, celery):
        self._backend = backend
        self._schedule_meta_list = []

    def initialize(self):
        pass

    def start(self):
        pass

    def enroll(self, *schedule_meta):
        pass

    def update(self, *schedule_meta):
        pass

    def remove(self, *schedule_meta):
        pass
