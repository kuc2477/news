from redis.exceptions import ConnectionError
from .utils.logging import logger
from .constants import (
    REDIS_PUBSUB_SLEEP_TIME,
    REDIS_SCHEDULE_CREATE_CHANNEL,
    REDIS_SCHEDULE_UPDATE_CHANNEL,
    REDIS_SCHEDULE_DELETE_CHANNEL,
)


class Persister(object):
    def __init__(self, redis, context=None):
        self.scheduler = None
        self.redis = redis
        self.pubsub = self.redis.pubsub()
        self.thread = None

        self._context = context
        self._cache = {}

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, ctx):
        self._context = ctx

    def start(self, scheduler, silent=False):
        if not self._redis_available():
            return

        self.scheduler = scheduler
        self.pubsub.subscribe(**{
            REDIS_SCHEDULE_CREATE_CHANNEL: lambda message:
            self.persist_save(int(message['data']), True),

            REDIS_SCHEDULE_UPDATE_CHANNEL: lambda message:
            self.persist_save(int(message['data']), False),

            REDIS_SCHEDULE_DELETE_CHANNEL: lambda message:
            self.persist_delete(int(message['data']))
        })
        self.thread = self.pubsub.run_in_thread(
            sleep_time=REDIS_PUBSUB_SLEEP_TIME)

    def stop(self):
        self.scheduler = None
        self.thread and self.thread.stop()

    # ====================
    # Schedule persistence
    # ====================

    def persist_save(self, id, created):
        if not self.scheduler:
            return

        # persist schedule in app context if given any
        if self.context:
            with self.context:
                created and self.scheduler.add(id, silent=False)
                not created and self.scheduler.update(id)
        # otherwise persist schedule without any context
        else:
            created and self.scheduler.add(id, silent=False)
            not created and self.scheduler.update(id)

    def persist_delete(self, id):
        if not self.scheduler:
            return

        # persist schedule in app context if given any
        if self.context:
            with self.context:
                self.scheduler.remove(id, silent=False)
        # otherwise persist schedule without any context
        else:
            self.scheduler.remove(id, silent=False)

    # ============================
    # Schedule change notification
    # ============================

    def notify_saved(self, instance, created, **kwargs):
        if self._redis_available():
            self.redis.publish(REDIS_SCHEDULE_CREATE_CHANNEL if created else
                               REDIS_SCHEDULE_UPDATE_CHANNEL, str(instance.id))

    def notify_deleted(self, instance, **kwargs):
        if self._redis_available():
            self.redis.publish(REDIS_SCHEDULE_DELETE_CHANNEL, str(instance.id))

    def _redis_available(self):
        if 'redis_available' in self._cache:
            return self._cache['redis_available']

        try:
            self.redis.get(None)
            available = True
        except ConnectionError:
            logger.warning(
                'Redis server for schedule persister is not available. This ' +
                'result will be cached and persistence won\'t be activated ' +
                'until you launch redis server for persister and restart ' +
                'your application'
            )
            available = False

        self._cache['redis_available'] = available
        return available

    def _flush_cache(self, name):
        return self._cache.pop(name)
