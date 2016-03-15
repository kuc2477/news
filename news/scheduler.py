""":mod:`news.scheduler` --- News scheduler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides scheduler that runs news cover celery tasks.

"""
import time
import threading
import schedule as pusher
from .constants import COVER_PUSHER_CYCLE
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
    :param persister: Persister that persists schedules via redis channel from
        backend. The persister that has been used when creating Schedule model
        with `create_schedule` factory method should be given. Note that the
        scheduler will not persist schedule changes if not given a persister.
    :type persister: :class:`news.persistence.SchedulePersister`
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

    *Example*::

        from celery import Celery
        from redis import Redis

        from django.contrib.auth.models import User
        from news.backends.django import DjangoBackend
        from news.models.django import (
            create_abc_schedule, create_abc_news,
            create_schedule, create_news
        )

        from news.scheduler import Scheduler
        from news.persistence import SchedulePersister


        redis = Redis()
        celery = Celery()
        persister = SchedulePersister(redis)

        Schedule = create_schedule(create_abc_schedule(User), persister)
        News = create_news(create_abc_news(Schedule))

        backend = DjangoBackend(User, Schedule, News)
        scheduler = Scheduler(backend, celery, persister=persister)
        scheduler.run()

    """
    def __init__(self, backend, celery, persister=None, intel_strategy=None,
                 report_experience=None, fetch_experience=None,
                 dispatch_middlewares=None, fetch_middlewares=None):
        self.backend = backend
        self.celery = celery
        self.celery_task = None

        self.persister = persister
        self.pusher = pusher
        self.jobs = dict()
        self.running = False

        self.intel_strategy = intel_strategy or (lambda backend, schedule: [])
        self.dispatch_middlewares = dispatch_middlewares or []
        self.fetch_middlewares = fetch_middlewares or []
        self.report_experience = report_experience
        self.fetch_experience = fetch_experience

    def run(self, persister=None):
        """
        Starts news cover scheduling in another tiny thread.

        :param persister: Persister that persists schedules from backend.
        :type persister: :class:`news.persistence.SchedulePersister`

        """
        if not self.celery_task:
            self.register_celery_task()

        if self.running:
            self.running = False
            self.clear_schedules()

        if persister:
            self.persister and self.persister.stop_persistence()
            self.persister = persister
        self.persister and self.persister.start_persistence(self)

        [self.add_schedule(s) for s in self.backend.get_schedules()]

        def runschedule():
            self.running = True
            while self.running:
                self.pusher.run_pending()
                time.sleep(COVER_PUSHER_CYCLE)

        threading.Thread(target=runschedule).start()

    def stop(self):
        """Stop news cover scheduling thread and schedule persistence."""
        self.persister and self.persister.stop_persistence()
        self.running = False

    def register_celery_task(self):
        @self.celery.task
        def run_cover(id):
            schedule = self.backend.get_schedule_by_id(id)
            intel = self.intel_strategy(self.backend, schedule)
            cover = Cover.from_schedule(schedule, self.backend)
            cover.prepare(
                intel=intel,
                report_experience=self.report_experience,
                fetch_experience=self.fetch_experience,
                dispatch_middlewares=self.dispatch_middlewares,
                fetch_middlewares=self.fetch_middlewares
            )
            cover.run()

        # expose celery task
        self.celery_task = run_cover

    def add_schedule(self, schedule):
        if isinstance(schedule, int):
            schedule = self.backend.get_schedule_by_id(schedule)

        self.jobs[schedule.id] = self.pusher\
            .every(schedule.cycle)\
            .seconds\
            .do(self.celery_task.delay, schedule.id)

    def remove_schedule(self, schedule):
        try:
            id = schedule.id
        except AttributeError:
            id = int(schedule)

        self.pusher.cancel_job(self.jobs.pop(id))

    def clear_schedules(self):
        [self.remove_schedule(id) for id in self.jobs.keys()]

    def update_schedule(self, schedule):
        self.remove_schedule(schedule)
        self.add_schedule(schedule)
