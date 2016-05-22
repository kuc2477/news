from celery.states import ALL_STATES


def test_abstract_model_implementations(sa_session, sa_schedule, sa_child_news):
    assert(isinstance(sa_schedule.id, int))
    assert(isinstance(sa_child_news.id, int))


def test_abstract_schedule_implementation(
        sa_scheduler, sa_session, sa_owner_model, sa_schedule):
    assert(isinstance(sa_schedule.owner, sa_owner_model))
    assert(isinstance(sa_schedule.url, str))
    assert(isinstance(sa_schedule.cycle, int))
    assert(isinstance(sa_schedule.options, dict))
    assert(sa_schedule.get_state(sa_scheduler.celery) in ALL_STATES)


def test_abstract_news_implementation(
        sa_session, sa_schedule, sa_root_news, sa_child_news):
    assert(isinstance(sa_child_news.url, str))
    assert(isinstance(sa_child_news.content, str))
    assert(isinstance(sa_child_news.title, str))
    assert(isinstance(sa_child_news.image, str) or sa_child_news.image is None)
    assert(isinstance(sa_child_news.summary, str) or
           sa_child_news.summary is None)

    assert(sa_root_news.schedule == sa_schedule)
    assert(sa_root_news.parent is None)
    assert(sa_root_news.root == sa_root_news)
    assert(sa_root_news.distance == 0)
    assert(sa_child_news.schedule == sa_schedule)
    assert(sa_child_news.parent == sa_root_news)
    assert(sa_child_news.root == sa_root_news)
    assert(sa_child_news.distance == 1)
