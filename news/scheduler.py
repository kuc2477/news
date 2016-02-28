""":mod: `news.schedule` --- Schedule related domain classes.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Provides schedule related domain classes which will be usually used by other
processes or threads in background.

"""
import schedule as worker

from .cover import Cover


class Scheduler(object):
    def __init__(self, backend, celery, intel_strategy=None,
                 report_experience=None, fetch_experience=None,
                 dispatch_middlewares=None, fetch_middlewares=None):
        self.backend = backend
        self.celery = celery
        self.jobs = dict()

        # reporter intel from past covers
        self.intel_strategy = intel_strategy or (lambda schedule, backend: [])

        # middlewares
        self.dispatch_middlewares = dispatch_middlewares or []
        self.fetch_middlewares = fetch_middlewares or []

        # reporter experience
        self.report_experience = report_experience
        self.fetch_experience = fetch_experience

        # set celery task
        self.run = self.celery.task(lambda cover: cover.run())

    def start(self):
        # start backend schedule persistence
        self._start_persistence()

        # start periodic jobs to push covers to the celery server.
        for schedule in self.backend.get_schedules():
            self.add_schedule(schedule)

    def _start_persistence(self):
        self.backend.set_schedule_save_listener(self._save_listener)
        self.backend.set_schedule_delete_listener(self._delete_listener)

    def _get_job(self, schedule):
        intel = self.intel_strategy(schedule, self.backend)
        cover = Cover.from_schedule(schedule, self.backend)
        cover.prepare(
            intel,
            report_experience=self.report_experience,
            fetch_experience=self.fetch_experience,
            dispatch_middlewares=self.dispatch_middlewares,
            fetch_middlewares=self.fetch_middlewares
        )
        return lambda: self.run.delay(cover)

    # ==================
    # Schedule modifiers
    # ==================

    def _add_schedule(self, schedule):
        self.jobs[schedule.id] = job = self._get_job(schedule)
        worker.every(schedule.cycle).minutes.do(job)

    def _remove_schedule(self, schedule):
        job = self.jobs[schedule.id]
        worker.cancel_job(job)
        del self.jobs[schedule.id]

    def _update_schedule(self, schedule):
        self.remove(schedule)
        self.add_schedule(schedule)

    # =============================================
    # Backend signal listeners to persist schedules
    # =============================================

    def _save_listener(self, instance, created):
        if created:
            self._add_schedule(instance)
        else:
            self._update_schedule(instance)

    def _delete_listener(self, instance):
        self._remove_schedule(instance)
