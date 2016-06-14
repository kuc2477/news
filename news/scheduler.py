""":mod:`news.scheduler` --- Scheduler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides a scheduler class that will run news cover celery tasks.

"""
import time
import threading
import schedule as pusher
from contextlib import contextmanager
from celery import Task, states
from .cover import Cover
from .mapping import DefaultMapping
from .utils.logging import logger
from .constants import COVER_PUSHER_CYCLE


class Scheduler(object):
    """Schedules news covers(:class:`~news.cover.Cover`) and keep in sync with
    backend schedules.

    :param backend: News backend to use.
    :type backend: :class:`news.backends.abstract.AbstractBackend`
        implementation.
    :param celery: Celery app instance to use as asynchronous job queue.
    :type celery: :class:`~celery.Celery`
    :param persister: Persister that persists schedules via redis channel from
        backend. The persister that has been used when creating Schedule model
        with `create_schedule` factory method should be given. Note that the
        scheduler will not persist schedule changes if not given.
    :type persister: :class:`news.persister.Persister`
    :param mapping: Schedule - Reporter class mapping to use. Default mapping
        which only supports 'rss', 'atom' and 'url' news type will be used
        if not given.
    :type mapping: :class:`news.mapping.Mapping`
    :param on_cover_start: Callback function that will be fired on cover start.
    :type on_cover_start: A function that takes a schedule
    :param on_cover_success: Callback function taht will be fired on cover
        success.
    :type on_cover_success: A function that takes a schedule and a list of
        result news of the cover.
    :param on_cover_failure: Callback function that will be fired on cover
        failure.
    :type on_cover_failre: A function that takes a schedule and an exception.

    **Example**::

        from redis import Redis
        from celery import Celery
        from django.contrib.auth.models import User
        from news.backends import DjangoBackend
        from news.scheduler import Scheduler
        from news.persister import Persister
        from news.models.django import (
            create_default_schedule,
            create_default_news,
        )

        # create a celery instance and a redis instance
        redis = Redis()
        celery = Celery()

        # create an persister (optional)
        persister = Persister(redis)

        # define models
        Schedule = create_default_schedule(
            user_model=User,
            persister=persister,
        )
        News = create_default_news(schedule_model=Schedule)

        # create a news backend
        backend = DjangoBackend(schedule_model=Schedule, news_model=News)

        # run a persisted scheduler
        scheduler = Scheduler(backend, celery, persister=persister)
        scheduler.start()

    """
    def __init__(self, backend=None, celery=None, mapping=None, persister=None,
                 on_cover_start=None, on_cover_success=None,
                 on_cover_failure=None,
                 request_middlewares=None, response_middlewares=None,
                 report_middlewares=None):
        # backend & celery
        self.backend = backend
        self.celery = celery
        self.celery_task = None
        self.mapping = DefaultMapping(mapping)

        # schedule persister and pusher
        self.persister = persister
        self.pusher = pusher

        # scheduler state
        self.jobs = dict()
        self.queued = set()
        self.running = False

        # scheduler cover callbacks
        self.on_cover_start = on_cover_start
        self.on_cover_success = on_cover_success
        self.on_cover_failure = on_cover_failure

        # reporter / cover middlewares
        self.request_middlewares = request_middlewares
        self.response_middlewares = response_middlewares
        self.report_middlewares = report_middlewares

    # =================
    # Scheduler actions
    # =================

    def configure(self, **kwargs):
        """Configure the schedule after the instantiation.

        :param **kwargs: Any constructor arguments to configure the scheduler.
        :type **kwargs: :class:`dict`
        :returns: Configured scheduler itself.
        :rtype: :class:`~news.scheduler.Scheduler`

        """
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self

    def start(self, persister=None):
        """Starts news cover scheduling in another tiny thread.

        :param persister: Persister that persists schedules from backend.
        :type persister: :class:`news.persister.Persister`

        """
        # set celery task if not set yet.
        if not self.celery_task:
            self.set_task()

        # stop and clear all schedule if the scheduler was already running.
        if self.running:
            self.running = False
            self.clear()

        # start schedule persistence if there's any persister available
        if persister:
            self.persister and self.persister.stop()
            self.persister = persister

        # start persistence if persister exists.
        if self.persister:
            self.persister.start(self)

        # add schedules
        schedules = self.backend.get_schedules()
        for schedule in schedules:
            self.add(schedule)
        self._log('Starting with {} schedule(s)'.format(len(schedules)))

        # start scheduler within a tiny thread.
        def schedule_forever():
            self.running = True
            self.pusher.run_all(delay_seconds=1)
            while self.running:
                self._log('Flush pending covers', tag='debug')
                self.pusher.run_pending()
                time.sleep(COVER_PUSHER_CYCLE)
        threading.Thread(target=schedule_forever).start()

    def stop(self):
        """Stop both the scheduler thread and the persister thread."""
        self.persister and self.persister.stop()
        self.running = False

    # ======================
    # Schedule manipulations
    # ======================

    def add(self, schedule, silent=True):
        """Add an schedule to the scheduler.

        :param schedule: An schedule or it's id to add to the scheduler.
        :type scheduke: :class:`news.models.AbstractSchedule` implementation or
            :int:

        """
        if not self.celery_task:
            self.set_task()

        if isinstance(schedule, int):
            schedule = self.backend.get_schedule(schedule)

        if not silent:
            self._log('Adding schedule {}'.format(schedule.id))

        self.jobs[schedule.id] = self.pusher\
            .every(schedule.cycle)\
            .minutes\
            .do(self._push_cover, schedule.id)

    def remove(self, schedule, silent=True):
        """Remove an schedule from the scheduler.

        Removal will fail silently if given schedule doesn't exist in the
        scheduler.

        :param schedule: An schedule or it's id to remove from the scheduler.
        :type schedule: :class:`news.models.AbstractSchedule` implementation or
            :int:

        """
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

    def clear(self):
        """Clear all registered schedules from the scheduler."""
        self._log('Clearing {} schedules'.format(len(self.jobs.keys())))
        [self.remove(id) for id in self.jobs.keys()]

    def update(self, schedule):
        """Update the registered schedule by reconciliating with database
        backend.

        :param schedule: Schedule to synchronize with the database.
        :type schedule: :class:`~news.models.AbstractSchedule` implementation

        """
        if isinstance(schedule, int):
            schedule = self.backend.get_schedule(schedule)

        # log
        self._log('Updating schedule {}'.format(
            schedule if isinstance(schedule, int) else schedule.id))

        # remove schedule from job queue and add it if it's now enabled
        self.remove(schedule)
        if schedule.enabled:
            self.add(schedule)

    # ==================
    # Celery integration
    # ==================

    def make_task(self):
        """Create an celery task responsible of running reporter covers
        asynchronously.

        :returns: An celery task.
        :rtype: :class:`~celery.Task`

        """
        class CallbackTask(Task):
            def on_success(task, retval, task_id, args, kwargs):
                schedule = self.backend.get_schedule(args[0])
                self.on_cover_success(schedule, retval)

            def on_failure(task, exc, task_id, args, kwargs, einfo):
                schedule = self.backend.get_schedule(args[0])
                self.on_cover_failure(schedule, exc)

        # make `run_cover` method into a celery task
        run_cover = self._make_run_cover()
        return self.celery.task(bind=True, base=CallbackTask)(run_cover)

    def set_task(self):
        """Set an celery task responsible of running reporter covers on the
        scheduler."""
        self.celery_task = self.make_task()

    def _make_cover(self, schedule):
        reporter_class, kwargs = self.mapping[schedule]
        cover = Cover(schedule=schedule, backend=self.backend)
        cover.prepare(
            reporter_class=reporter_class,
            request_middlewares=self.request_middlewares,
            response_middlewares=self.response_middlewares,
            **kwargs
        )
        return cover

    def _make_run_cover(self):
        def run_cover(task, id):
            # mark task state started
            task.update_state(states.STARTED)

            # retrieve a schedule and make cover from it
            schedule = self.backend.get_schedule(id)
            cover = self._make_cover(schedule)

            # pop from task queue indicator
            if id in self.queued:
                self.queued.remove(id)

            # run news cover along with registered callbacks
            sl = 'Cover for schedule {} starting'.format(id)
            fl = 'Cover for schedule{} finished'.format(id)
            with self._log_ctx(sl, fl, t1='debug', t2='debug'):
                if self.on_cover_start:
                    self.on_cover_start(schedule)
                cover.run()

        return run_cover

    def _push_cover(self, id):
        # do not push cover into task queue if already exists
        if not self.celery_task or id in self.queued:
            return
        self._log('pushing schedule {}'.format(id), tag='warning')
        self.celery_task.apply_async((id,), task_id=str(id))
        self.queued.add(id)

    def _log(self, message, tag='info'):
        logging_method = getattr(logger, tag)
        logging_method('[Scheduler]: {}'.format(message))

    @contextmanager
    def _log_ctx(self, l1, l2, t1='info', t2='info'):
        self._log(l1, tag=t1)
        yield
        self._log(l2, tag=t2)
