""":mod: `news.schedule` --- Schedule related domain classes.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Provides schedule related domain classes which will be usually used by other
processes or threads in background.

"""
import schedule as worker

from .cover import Cover


class Scheduler(object):
    def __init__(self, backend, celery):
        self.backend = backend
        self.celery = celery
        self.jobs = dict()
        self.run = self.celery.task(lambda cover: cover.run())

    def start(self):
        # start backend schedule persistence
        self.start_persistence()

        # start periodic jobs to push covers to the celery server.
        for schedule in self.backend.get_schedules():
            self.add_schedule(schedule)

    def start_persistence(self):
        self.backend.set_schedule_save_listener(self._save_listener)
        self.backend.set_schedule_delete_listener(self._delete_listener)

    def get_job(self, schedule):
        cover = Cover.from_schedule(schedule, self.backend)
        return lambda: self.run.delay(cover)

    # ==================
    # Schedule modifiers
    # ==================

    def add_schedule(self, schedule):
        self.jobs[schedule.id] = job = self.get_job(schedule)
        worker.every(schedule.cycle).minutes.do(job)

    def remove_schedule(self, schedule):
        job = self.jobs[schedule.id]
        worker.cancel_job(job)
        del self.jobs[schedule.id]

    def update_schedule(self, schedule):
        self.remove(schedule)
        self.add_schedule(schedule)

    # =============================================
    # Backend signal listeners to persist schedules
    # =============================================

    def _save_listener(self, instance, created):
        if created:
            self.add_schedule(instance)
        else:
            self.update_schedule(instance)

    def _delete_listener(self, instance):
        self.remove_schedule(instance)
