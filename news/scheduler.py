""":mod:`news.scheduler` --- News scheduler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides scheduler that runs news cover celery tasks.

"""
import time
import threading
import schedule as worker
from .cover import Cover


class Scheduler(object):
    """
    Schedules news covers(:class:`~news.cover.Cover`) and keep in sync with
    backend schedules.

    :param backend: News backend to use.
    :type backend: :class:`news.backends.abstract.AbstractBackend`
        implementation.
    :param celery: Celery app instance to use as asynchronous job queue.
    :type celery: :class:`~celery.Celery`
    :param intel_strategy: Intel strategy to use for a schedule. Using nicely
        implemented intel strategy function can be work as performance boost
        in news fetching processes since reporters in charge of the given
        intel will be batch-dispatched rather than wating for their
        predecessors to dispatch them.
    :type intel_strategy: A function that takes a schedule and the backend of
        the scheduler as positional arguments and return a list of news.
    :param report_experience: Module qualified path to the report experience
        function. The report experience function should take a schedule of the
        news and the news as it's arguments  and return `True` if the news is
        valuable.  Otherwise it should return `False`.
    :type report_experience: :class:`str`
    :param fetch_experience: Module qualified path to the fetch experience
        function. The fetch experience function should take a schedule of the
        news, the news and the url to be classified whether it is worth to
        visit or not. The function should return `True` if the url is expected
        to be worthy. Otherwise it should return `False`.
    :type fetch_experience: :class:`str`
    :param dispatch_middlewares: A list of module qualified paths to dispatch
        middlewares to use. The dispatch middlewares should take a reporter(
        :class:`~news.reporter.Reporter`) and it's
        :func:`~news.reporter.Reporter.dispatch` method and return enhanced
        dispatch method. Note that the middlewares will be only applied to
        the root(chief) reporter and won't be inherited down to it's successor
        reporters.
    :type dispatch_middlewares: :class:`list`
    :param fetch_middlewares: A list of module qualified paths to fetch
        middlewares to use. The fetch middlewares should take a reporter(
        :class:`~news.reporter.Reporter`) and it's
        :func:`~news.reporter.Reporter.fetch` method and return enhanced
        fetch method. Not that the middlewares will be applied down to
        the successor reporters of the chief reporter.
    :type  fetch_middlewares: :class:`list`

    """
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
        """Starts backend persistence and news cover scheduling on another
        thread"""
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
        """Stops news cover scheduling that was running on another thread"""
        self._scheduling = False

    def clear(self):
        """Clear all jobs that were scheduled and pending to be dispatched"""
        pass

    def _schedule_forever(self):
        while self._scheduling:
            worker.run_pending()
            time.sleep(1)

    def _start_persistence(self):
        self.backend.set_schedule_save_listener(self._save_listener)
        self.backend.set_schedule_delete_listener(self._delete_listener)

    def _get_cover(self, schedule):
        intel = self.intel_strategy(schedule, self.backend) if \
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
