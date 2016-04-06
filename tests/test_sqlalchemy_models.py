import uuid


def test_abstract_model_implementations(sa_session, sa_schedule, sa_news):
    assert(isinstance(sa_schedule.id, int))
    assert(isinstance(sa_news.id, int))


def test_abstract_schedule_implementation(
        sa_session, sa_owner_model, sa_schedule):
    assert(isinstance(sa_schedule.owner, sa_owner_model))
    assert(isinstance(sa_schedule.url, str))
    assert(isinstance(sa_schedule.cycle, int))
    assert(isinstance(sa_schedule.filter_options, dict))
    assert(isinstance(sa_schedule.latest_task, str) or
           sa_schedule.latest_task is None)

    task_id = uuid.uuid4()
    sa_schedule.update_latest_task(task_id)
    assert(sa_schedule.latest_task == task_id)


def test_abstract_news_implementation(
        sa_session, sa_schedule, sa_root_news, sa_news):
    assert(isinstance(sa_news.url, str))
    assert(isinstance(sa_news.content, str))
    assert(isinstance(sa_news.title, str))
    assert(isinstance(sa_news.image, str) or sa_news.image is None)
    assert(isinstance(sa_news.description, str) or
           sa_news.description is None)

    assert(sa_root_news.schedule == sa_schedule)
    assert(sa_root_news.src is None)
    assert(sa_root_news.root == sa_root_news)
    assert(sa_root_news.depth == 0)
    assert(sa_root_news.distance == 0)

    assert(sa_news.schedule == sa_schedule)
    assert(sa_news.src == sa_root_news)
    assert(sa_news.root == sa_root_news)
    assert(sa_news.depth == 1)
    assert(sa_news.distance == 1)
