from time import sleep
from news.constants import REDIS_PUBSUB_SLEEP_TIME


def test_schedule_update(mocker, sa_session, sa_schedule,
                         sa_scheduler, persister):
    persister.persist_save = lambda *args, **kwargs: None
    mocker.spy(persister, 'notify_saved')
    mocker.spy(persister, 'persist_save')
    persister.start(sa_scheduler)

    assert(not persister.notify_saved.called)
    assert(not persister.persist_save.called)

    sa_schedule.url = 'changed'
    sa_session.commit()

    sleep(REDIS_PUBSUB_SLEEP_TIME * 20)
    assert(persister.notify_saved.called)
    assert(persister.persist_save.called)
    persister.stop()


def test_schedule_create(mocker, sa_session, sa_schedule_model, sa_owner,
                         sa_scheduler, persister):
    persister.persist_save = lambda *args, **kwargs: None
    mocker.spy(persister, 'notify_saved')
    mocker.spy(persister, 'persist_save')
    persister.start(sa_scheduler)

    assert(not persister.notify_saved.called)
    assert(not persister.persist_save.called)

    schedule = sa_schedule_model(owner=sa_owner, url='new')
    sa_session.add(schedule)
    sa_session.commit()

    sleep(REDIS_PUBSUB_SLEEP_TIME * 20)
    assert(persister.notify_saved.called)
    assert(persister.persist_save.called)
    persister.stop()


def test_schedule_delete(mocker, sa_session, sa_schedule,
                         persister, sa_scheduler):
    persister.persist_delete = lambda *args, **kwargs: None
    mocker.spy(persister, 'notify_deleted')
    mocker.spy(persister, 'persist_delete')
    persister.start(sa_scheduler)

    assert(not persister.notify_deleted.called)
    assert(not persister.persist_delete.called)

    sa_session.delete(sa_schedule)
    sa_session.commit()

    sleep(REDIS_PUBSUB_SLEEP_TIME * 20)
    assert(persister.notify_deleted.called)
    assert(persister.persist_delete.called)
    persister.stop()
