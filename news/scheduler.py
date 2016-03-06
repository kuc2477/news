""":mod:`news.scheduler` --- News scheduler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides scheduler that runs news subscription on celery tasks.

"""
import time
import threading
import schedule as worker
from .cover import Cover
from .utils.python import importattr


class Scheduler(object):
    def __init__(self, backend, celery, intel_strategy=None,
                 report_experience=None, fetch_experience=None,
                 dispatch_middlewares=None, fetch_middlewares=None):
        self.backend = backend
        self.celery = celery
        self.jobs = dict()

        self._scheduling = False

        # reporter intel from past covers
        self.intel_strategy = intel_strategy

        # middlewares
        self.dispatch_middlewares = dispatch_middlewares or []
        self.fetch_middlewares = fetch_middlewares or []

        # reporter experience
        self.report_experience = report_experience
        self.fetch_experience = fetch_experience

        # set run celery task
        self.run = self.celery.task(lambda cover: cover.run())

    def start(self):
        # start backend schedule persistence
        self._start_persistence()

        # add periodic jobs to the worker(scheduler) to push covers to
        # celery server.
        for schedule in self.backend.get_schedules():
            self._add_schedule(schedule)

        # start scheduling
        self._scheduling = True
        thread = threading.Thread(target=self._schedule_forever, args=())
        thread.daemon = True
        thread.start()

    def stop(self):
        self._scheduling = False

    def clear(self):
        pass

    def _schedule_forever(self):
        while self._scheduling:
            worker.run_pending()
            time.sleep(1)

    def _start_persistence(self):
        self.backend.set_schedule_save_listener(self._save_listener)
        self.backend.set_schedule_delete_listener(self._delete_listener)

    def _get_cover(self, schedule):
        intel = importattr(self.intel_strategy)(schedule, self.backend) if \
            self.intel_strategy else []
        cover = Cover.from_schedule(schedule, self.backend)
        cover.prepare(
            intel,
            report_experience=self.report_experience,
            fetch_experience=self.fetch_experience,
            dispatch_middlewares=self.dispatch_middlewares,
            fetch_middlewares=self.fetch_middlewares
        )
        return cover

    # ==================
    # Schedule modifiers
    # ==================

    def _add_schedule(self, schedule):
        cover = self._get_cover(schedule)
        self.jobs[schedule.id] = \
            worker.every(schedule.cycle).minutes.do(self.run, cover)

    def _remove_schedule(self, schedule):
        worker.cancel_job(self.jobs.pop(schedule.id))

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
