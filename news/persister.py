from redis.exceptions import ConnectionError
from .utils.logging import logger
from .constants import (
    REDIS_PUBSUB_SLEEP_TIME,
    REDIS_SCHEDULE_CREATE_CHANNEL,
    REDIS_SCHEDULE_UPDATE_CHANNEL,
    REDIS_SCHEDULE_DELETE_CHANNEL,
)


class Persister(object):
    def __init__(self, redis):
        self.scheduler = None
        self.redis = redis
        self.pubsub = self.redis.pubsub()
        self.thread = None

        self._cache = {}

    def start_persistence(self, scheduler, silent=False):
        if not self._redis_available():
            return

        self.scheduler = scheduler
        self.pubsub.subscribe(**{
            REDIS_SCHEDULE_CREATE_CHANNEL: lambda message:
            self.persist_schedule_save(int(message['data']), True),

            REDIS_SCHEDULE_UPDATE_CHANNEL: lambda message:
            self.persist_schedule_save(int(message['data']), False),

            REDIS_SCHEDULE_DELETE_CHANNEL: lambda message:
            self.persist_schedule_delete(int(message['data']))
        })
        self.thread = self.pubsub.run_in_thread(
            sleep_time=REDIS_PUBSUB_SLEEP_TIME)

    def stop_persistence(self):
        self.scheduler = None
        self.thread and self.thread.stop()

    def persist_schedule_save(self, id, created):
        if self.scheduler:
            created and self.scheduler.add_schedule(id)
            not created and self.scheduler.update_schedule(id)

    def persist_schedule_delete(self, id):
        if self.scheduler:
            self.scheduler.remove_schedule(id)

    def notify_schedule_saved(self, instance, created, **kwargs):
        if self._redis_available():
            self.redis.publish(REDIS_SCHEDULE_CREATE_CHANNEL if created else
                               REDIS_SCHEDULE_UPDATE_CHANNEL, str(instance.id))

    def notify_schedule_deleted(self, instance, **kwargs):
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
