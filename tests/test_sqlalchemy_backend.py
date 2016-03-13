def test_get_news(sa_session, sa_backend, sa_news):
    url = sa_news.url
    owner = sa_news.owner
    assert(sa_news == sa_backend.get_news(owner, url))
    assert(sa_backend.get_news(None, '') is None)


def test_get_news_list(sa_session, sa_backend, sa_news):
    assert(sa_news in sa_backend.get_news_list())
    assert(sa_news in sa_backend.get_news_list(owner=sa_news.owner))
    assert(sa_news in sa_backend.get_news_list(root_url=sa_news.root.url))
    assert(sa_news in sa_backend.get_news_list(
        owner=sa_news.owner,
        root_url=sa_news.root.url
    ))


def test_news_exists(sa_session, sa_backend, sa_news):
    url = sa_news.url
    owner = sa_news.owner

    assert(sa_backend.news_exists(owner, url))
    sa_backend.delete_news(sa_news)
    assert(not sa_backend.news_exists(owner, url))


def test_save_news(sa_session, sa_backend,
                   sa_schedule, sa_news_model, url_root, content_root):
    news = sa_news_model.create_instance(
        schedule=sa_schedule,
        url=url_root,
        content=content_root
    )
    assert(sa_backend.get_news(sa_schedule.owner, url_root) is None)
    sa_backend.save_news(news)
    assert(news in sa_backend.get_news_list(sa_schedule.owner, url_root))


def test_delete_news(sa_session, sa_backend, sa_news):
    assert(sa_backend.news_exists(sa_news.owner, sa_news.url))
    sa_backend.delete_news(sa_news)
    assert(not sa_backend.news_exists(sa_news.owner, sa_news.url))


def test_get_schedule_by_id(sa_session, sa_backend, sa_schedule):
    assert(sa_schedule == sa_backend.get_schedule_by_id(sa_schedule.id))


def test_get_schedule(sa_session, sa_backend, sa_schedule):
    assert(sa_schedule ==
           sa_backend.get_schedule(sa_schedule.owner, sa_schedule.url))


def test_get_schedules(sa_session, sa_backend, sa_schedule,
                       sa_owner, url_root):
    assert(sa_schedule in sa_backend.get_schedules(sa_owner, url_root))


def test_set_schedule_save_listener_create(
        mocker, sa_session, sa_backend, sa_owner, sa_schedule_model, url):
    stub = mocker.stub()
    sa_backend.set_schedule_save_listener(stub)

    schedule = sa_schedule_model(url=url, owner=sa_owner)
    sa_session.add(schedule)
    sa_session.commit()

    stub.assert_called_once_with(schedule, created=True)


def test_set_schedule_save_listener_update(mocker, sa_session, sa_backend,
                                           sa_schedule):
    stub = mocker.stub()
    sa_backend.set_schedule_save_listener(stub)
    sa_schedule.url = 'changed_url'
    sa_session.commit()

    stub.assert_called_once_with(sa_schedule, created=False)


def test_set_schedule_delete_listener(mocker, sa_session, sa_backend,
                                      sa_schedule):
    stub = mocker.stub()
    sa_backend.set_schedule_delete_listener(stub)
    sa_session.delete(sa_schedule)
    sa_session.commit()

    stub.assert_called_once_with(sa_schedule)
