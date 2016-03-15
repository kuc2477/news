import platform
import pytest


@pytest.mark.skipif(platform.system().lower() == 'windows',
                    reason='celery service test won\'t run in windows')
def test_run(scheduler, django_schedule):
    scheduler.register_celery_task()
    scheduler.celery_task.delay(django_schedule.id)


def test_add_schedule(scheduler, django_schedule):
    assert(not scheduler.jobs)
    scheduler.add_schedule(django_schedule)
    assert(scheduler.jobs)


def test_remove_schedule(scheduler, django_schedule):
    scheduler.add_schedule(django_schedule)
    assert(scheduler.jobs)
    scheduler.remove_schedule(django_schedule)
    assert(not scheduler.jobs)
