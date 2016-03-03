def test_get_news(sa_session, sa_backend, sa_news):
    url = sa_news.url
    owner = sa_news.schedule.owner
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
    owner = sa_news.schedule.owner

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
    assert(news not in sa_backend.get_news_list(sa_schedule.owner, url_root))
    sa_backend.save_news(news)
    assert(news in sa_backend.get_news_list(sa_schedule.owner, url_root))
