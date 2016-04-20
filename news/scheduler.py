""":mod:`news.scheduler` --- News scheduler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides scheduler that runs news cover celery tasks.

"""
import time
import threading
import schedule as pusher
from .constants import COVER_PUSHER_CYCLE
from .cover import Cover
from .utils.logging import logger


class Scheduler(object):
    """
    Schedules news covers(:class:`~news.cover.Cover`) and keep in sync with
    backend schedules.

    :param backend: News backend to use.
    :type backend: :class:`news.backends.AbstractBackend`
        implementation.
    :param celery: Celery app instance to use as asynchronous job queue.
    :type celery: :class:`~celery.Celery`
    :param persister: Persister that persists schedules via redis channel from
        backend. The persister that has been used when creating Schedule model
        with `create_schedule` factory method should be given. Note that the
        scheduler will not persist schedule changes if not given a persister.
    :type persister: :class:`news.persister.Persister`
    :param intel_strategy: Intel strategy to use for a schedule. Using nicely
        implemented intel strategy function can be work as performance boost
        in news fetching processes since reporters in charge of the given
        intel will be batch-dispatched rather than wating for their
        predecessors to dispatch them.
    :type intel_strategy: A function that takes a schedule and the backend of
        the scheduler as positional arguments and return a list of news.
    :param on_cover_start: Callback function that will be fired on cover start.
    :type on_cover_start: A function that takes a schedule
    :param on_cover_finished: Callback function taht will be fired on cover
        finish.
    :type on_cover_finished: A function that takes a schedule and a list of
        result news of the cover.
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
    def __init__(self, backend=None, celery=None,
                 persister=None, intel_strategy=None,
                 on_cover_start=None, on_cover_finished=None,
                 report_experience=None, fetch_experience=None,
                 dispatch_middlewares=None, fetch_middlewares=None):
        # backend & celery
        self.backend = backend
        self.celery = celery
        self.celery_task = None

        # schedule persister and pusher
        self.persister = persister
        self.pusher = pusher

        # scheduler state
        self.jobs = dict()
        self.running = False

        # scheduler intel strategy
        self.intel_strategy = intel_strategy or (lambda backend, schedule: [])

        # scheduler cover callbacks
        self.on_cover_start = on_cover_start or (lambda schedule: None)
        self.on_cover_finished = \
            on_cover_finished or (lambda schedule, news_list: None)

        # scheduler middlewares
        self.dispatch_middlewares = dispatch_middlewares or []
        self.fetch_middlewares = fetch_middlewares or []

        # reporter experience to use
        self.report_experience = report_experience
        self.fetch_experience = fetch_experience

    # =================
    # Scheduler actions
    # =================

    def configure(self, **kwargs):
        self.__init__(**kwargs)

    def start(self, persister=None):
        """
        Starts news cover scheduling in another tiny thread.

        :param persister: Persister that persists schedules from backend.
        :type persister: :class:`news.persister.Persister`

        """
        if not self.celery_task:
            self.set_task()

        if self.running:
            self.running = False
            self.clear_schedules()

        # start schedule persistence if there's any persister available
        if persister:
            self.persister and self.persister.stop_persistence()
            self.persister = persister
        self.persister and self.persister.start_persistence(self)

        schedules = self.backend.get_schedules()
        [self.add_schedule(s) for s in schedules]
        self._log('Starting with {} schedule(s)'.format(len(schedules)))

        def schedule_forever():
            self.running = True
            while self.running:
                self._log('Flush pending covers', tag='debug')
                self.pusher.run_pending()
                time.sleep(COVER_PUSHER_CYCLE)

        threading.Thread(target=schedule_forever).start()

    def stop(self):
        """Stop news cover scheduling thread and schedule persistence."""
        self.persister and self.persister.stop_persistence()
        self.running = False

    # ===================
    # Celery integration
    # ===================

    def make_run_cover(self):
        def run_cover(task, id):
            # update latest task
            schedule = self.backend.get_schedule_by_id(id)
            schedule.update_latest_task(task.request.id)
            self._log('Cover for schedule {} starting'.format(schedule.id))

            # prepare news cover with preconfigured experience and middlewares.
            intel = self.intel_strategy(self.backend, schedule)
            cover = Cover.from_schedule(schedule, self.backend)
            cover.prepare(
                intel=intel,
                report_experience=self.report_experience,
                fetch_experience=self.fetch_experience,
                dispatch_middlewares=self.dispatch_middlewares,
                fetch_middlewares=self.fetch_middlewares
            )
            # run news cover along with registered callbacks
            self.on_cover_start(schedule)
            self.on_cover_finished(schedule, cover.run())
            self._log('Cover for schedule {} finished'.format(schedule.id))
        return run_cover

    def make_task(self):
        return self.celery.task(bind=True)(self.make_run_cover())

    def set_task(self):
        self.celery_task = self.make_task()

    # ======================
    # Schedule manipulations
    # ======================

    def add_schedule(self, schedule, silent=True):
        if not self.celery_task:
            self.set_task()

        if isinstance(schedule, int):
            schedule = self.backend.get_schedule_by_id(schedule)

        if not silent:
            self._log('Adding schedule {}'.format(schedule.id))

        self.jobs[schedule.id] = self.pusher\
            .every(schedule.cycle)\
            .seconds\
            .do(self.celery_task.delay, schedule.id)

    def remove_schedule(self, schedule, silent=True):
        try:
            id = schedule.id
        except AttributeError:
            id = int(schedule)

        if not silent:
            self._log('Removing schedule {}'.format(id))

        try:
            self.pusher.cancel_job(self.jobs.pop(id))
        except KeyError:
            pass

    def clear_schedules(self):
        self._log('Clearing {} schedules'.format(len(self.jobs.keys())))
        [self.remove_schedule(id) for id in self.jobs.keys()]

    def update_schedule(self, schedule):
        self._log(
            'Updating schedule {}'
            .format(schedule if isinstance(schedule, int)
                    else schedule.id)
        )

        if not schedule.enabled:
            self.remove_schedule(schedule)
        else:
            self.remove_schedule(schedule)
            self.add_schedule(schedule)

    def _log(self, message, tag='info'):
        logging_method = getattr(logger, tag)
        logging_method('[Scheduler]: {}'.format(message))
