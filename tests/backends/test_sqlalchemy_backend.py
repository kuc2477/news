def test_get_news(sa_session, sa_backend, sa_child_news):
    assert(sa_child_news == sa_backend.get_news(sa_child_news.id))
    assert(sa_backend.get_news(None) is None)


def test_get_news_list(sa_session, sa_backend, sa_child_news):
    assert(sa_child_news in sa_backend.get_news_list())
    assert(sa_child_news in sa_backend.get_news_list(
        owner=sa_child_news.owner))
    assert(sa_child_news in sa_backend.get_news_list(
        root_url=sa_child_news.root.url))
    assert(sa_child_news in sa_backend.get_news_list(
        owner=sa_child_news.owner,
        root_url=sa_child_news.root.url
    ))


def test_news_exists(sa_session, sa_backend, sa_child_news):
    assert(sa_backend.news_exists(sa_child_news.id))
    sa_backend.delete_news(sa_child_news)
    assert(not sa_backend.news_exists(sa_child_news.id))


def test_save_news(sa_session, sa_backend,
                   sa_schedule, sa_news_model, url_root, content_root):
    news = sa_news_model.create_instance(
        schedule=sa_schedule,
        url=url_root,
        title='title',
        content=content_root,
        summary='summary'
    )
    assert(news not in sa_backend.get_news_list(sa_schedule.owner, url_root))
    sa_backend.save_news(news)
    assert(news in sa_backend.get_news_list(sa_schedule.owner, url_root))


def test_delete_news(sa_session, sa_backend, sa_child_news):
    assert(sa_backend.news_exists(sa_child_news.id))
    sa_backend.delete_news(sa_child_news)
    assert(not sa_backend.news_exists(sa_child_news.id))


def test_get_schedule(sa_session, sa_backend, sa_schedule):
    assert(sa_schedule == sa_backend.get_schedule(sa_schedule.id))


def test_get_schedules(sa_session, sa_backend, sa_schedule,
                       sa_owner, url_root):
    assert(sa_schedule in sa_backend.get_schedules(sa_owner, url_root))
