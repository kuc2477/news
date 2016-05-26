from celery.states import ALL_STATES


def test_abstract_model_implementations(django_schedule, django_child_news):
    assert(isinstance(django_schedule.id, int))
    assert(isinstance(django_child_news.id, int))


def test_abstract_schedule_implementation(
        django_scheduler, django_backend, django_schedule):
    assert(isinstance(django_schedule.url, str))
    assert(isinstance(django_schedule.cycle, int))
    assert(isinstance(django_schedule.options, dict))
    assert(django_schedule.get_state(django_scheduler.celery) in ALL_STATES)


def test_abstract_news_implementation(django_backend, django_schedule,
                                      django_child_news, django_root_news):
    assert(isinstance(django_child_news.url, str))
    assert(isinstance(django_child_news.content, str))
    assert(isinstance(django_child_news.schedule, django_backend.Schedule))
    assert(isinstance(django_child_news.parent, django_backend.News))
    assert(django_child_news.parent == django_root_news)
    assert(django_root_news.parent is None)
    assert(django_child_news.owner == django_schedule.owner)
    assert(isinstance(django_child_news.title, str))
    assert(isinstance(django_child_news.image, str) or 
           django_child_news.image is None)
    assert(isinstance(django_child_news.summary, str) or
           django_child_news.summary is None)

    assert(not django_child_news.is_root)
    assert(django_child_news.distance == 1)
    assert(django_root_news.is_root)
    assert(django_root_news.distance == 0)
