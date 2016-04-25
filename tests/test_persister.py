from time import sleep
from news.constants import REDIS_PUBSUB_SLEEP_TIME


def test_schedule_update(mocker, sa_session, sa_schedule,
                         sa_scheduler, persister):
    persister.persist_schedule_save = lambda *args, **kwargs: None
    mocker.spy(persister, 'notify_schedule_saved')
    mocker.spy(persister, 'persist_schedule_save')
    persister.start_persistence(sa_scheduler)

    assert(not persister.notify_schedule_saved.called)
    assert(not persister.persist_schedule_save.called)

    sa_schedule.url = 'changed'
    sa_session.commit()

    sleep(REDIS_PUBSUB_SLEEP_TIME * 20)
    assert(persister.notify_schedule_saved.called)
    assert(persister.persist_schedule_save.called)
    persister.stop_persistence()


def test_schedule_create(mocker, sa_session, sa_schedule_model, sa_owner,
                         sa_scheduler, persister):
    persister.persist_schedule_save = lambda *args, **kwargs: None
    mocker.spy(persister, 'notify_schedule_saved')
    mocker.spy(persister, 'persist_schedule_save')
    persister.start_persistence(sa_scheduler)

    assert(not persister.notify_schedule_saved.called)
    assert(not persister.persist_schedule_save.called)

    schedule = sa_schedule_model(owner=sa_owner, url='new')
    sa_session.add(schedule)
    sa_session.commit()

    sleep(REDIS_PUBSUB_SLEEP_TIME * 20)
    assert(persister.notify_schedule_saved.called)
    assert(persister.persist_schedule_save.called)
    persister.stop_persistence()


def test_schedule_delete(mocker, sa_session, sa_schedule,
                         persister, sa_scheduler):
    persister.persist_schedule_delete = lambda *args, **kwargs: None
    mocker.spy(persister, 'notify_schedule_deleted')
    mocker.spy(persister, 'persist_schedule_delete')
    persister.start_persistence(sa_scheduler)

    assert(not persister.notify_schedule_deleted.called)
    assert(not persister.persist_schedule_delete.called)

    sa_session.delete(sa_schedule)
    sa_session.commit()

    sleep(REDIS_PUBSUB_SLEEP_TIME * 20)
    assert(persister.notify_schedule_deleted.called)
    assert(persister.persist_schedule_delete.called)
    persister.stop_persistence()
