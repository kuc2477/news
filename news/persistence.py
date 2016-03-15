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

    def start_persistence(self, scheduler):
        self.scheduler = scheduler
        self.pubsub.subscribe(**{
            REDIS_SCHEDULE_CREATE_CHANNEL: lambda message:
            self.persist_schedule_save(int(message), True),

            REDIS_SCHEDULE_UPDATE_CHANNEL: lambda message:
            self.persist_schedule_save(int(message), False),

            REDIS_SCHEDULE_DELETE_CHANNEL: lambda message:
            self.persist_schedule_delete(int(message))
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
        self.scheduler and self.scheduler.remove_schedule(id)

    def notify_schedule_saved(self, instance, created):
        self.redis.publish(REDIS_SCHEDULE_CREATE_CHANNEL if created else
                           REDIS_SCHEDULE_UPDATE_CHANNEL, str(instance.id))

    def notify_schedule_deleted(self, instance):
        self.redis.publish(REDIS_SCHEDULE_DELETE_CHANNEL, str(instance.id))
