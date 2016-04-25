import celery


def test_run(scheduler, django_schedule):
    scheduler.set_task()
    assert(isinstance(scheduler.celery_task, celery.Task))


def test_add_schedule(scheduler, django_schedule):
    assert(not scheduler.jobs)
    scheduler.add_schedule(django_schedule)
    assert(scheduler.jobs)


def test_remove_schedule(scheduler, django_schedule):
    scheduler.add_schedule(django_schedule)
    assert(scheduler.jobs)
    scheduler.remove_schedule(django_schedule)
    assert(not scheduler.jobs)
