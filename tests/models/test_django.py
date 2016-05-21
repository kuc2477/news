from celery.states import ALL_STATES


def test_abstract_model_implementations(django_schedule, django_news):
    assert(isinstance(django_schedule.id, int))
    assert(isinstance(django_news.id, int))


def test_abstract_schedule_implementation(
        scheduler, django_backend, django_schedule):
    assert(isinstance(django_schedule.owner, django_backend.Owner))
    assert(isinstance(django_schedule.url, str))
    assert(isinstance(django_schedule.cycle, int))
    assert(isinstance(django_schedule.latest_task, str) or
           django_schedule.latest_task is None)
    assert(isinstance(django_schedule.filter_options, dict))
    assert(django_schedule.get_state(scheduler.celery) in ALL_STATES)


def test_abstract_news_implementation(django_backend, django_schedule,
                                      django_news, django_root_news):
    assert(isinstance(django_news.url, str))
    assert(isinstance(django_news.content, str))
    assert(isinstance(django_news.schedule, django_backend.Schedule))
    assert(isinstance(django_news.src, django_backend.News))
    assert(django_news.src == django_root_news)
    assert(django_root_news.src is None)
    assert(django_news.owner == django_schedule.owner)
    assert(django_news.root == django_root_news)
    assert(django_root_news.root == django_root_news)
    assert(django_root_news.depth == 0)
    assert(django_root_news.distance == 0)
    assert(django_news.distance == 1)
    assert(isinstance(django_news.title, str))
    assert(isinstance(django_news.image, str) or django_news.image is None)
    assert(isinstance(django_news.description, str) or
           django_news.description is None)
