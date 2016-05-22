import celery


def test_run(django_scheduler, django_schedule):
    django_scheduler.set_task()
    assert(isinstance(django_scheduler.celery_task, celery.Task))


def test_add_schedule(django_scheduler, django_schedule):
    assert(not django_scheduler.jobs)
    django_scheduler.add(django_schedule)
    assert(django_scheduler.jobs)


def test_remove_schedule(django_scheduler, django_schedule):
    django_scheduler.add(django_schedule)
    assert(django_scheduler.jobs)
    django_scheduler.remove(django_schedule)
    assert(not django_scheduler.jobs)
