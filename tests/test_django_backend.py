import pytest


@pytest.mark.django_db
def test_get_news(django_backend, django_news):
    assert(django_news == django_backend.get_news(django_news.id))
    assert(django_backend.get_news(None) is None)


@pytest.mark.django_db
def test_get_news_list(django_backend, django_news):
    assert(django_news in django_backend.get_news_list())
    assert(django_news in
           django_backend.get_news_list(owner=django_news.owner))
    assert(django_news in
           django_backend.get_news_list(root_url=django_news.root.url))
    assert(django_news in
           django_backend.get_news_list(
               owner=django_news.owner,
               root_url=django_news.root.url
           ))


@pytest.mark.django_db
def test_news_exists(django_backend, django_news):
    url = django_news.url
    owner = django_news.schedule.owner

    assert(django_backend.news_exists_by(owner, url))
    django_backend.delete_news(django_news)
    assert(not django_backend.news_exists_by(owner, url))


@pytest.mark.django_db
def test_save_news(django_backend, django_schedule, django_news_model,
                   url, content):
    news = django_news_model(
        schedule=django_schedule,
        url=url,
        content=content
    )
    url = news.url
    owner = news.schedule.owner

    assert(not django_backend.news_exists_by(owner, url))
    django_backend.save_news(news)
    assert(django_backend.news_exists_by(owner, url))


@pytest.mark.django_db
def test_cascade_save_news(django_backend, django_schedule, django_news_model,
                           url_root, content_root, url_child, content_child):
    root = django_news_model(
        schedule=django_schedule,
        url=url_root,
        content=content_root
    )
    child = django_news_model(
        schedule=django_schedule,
        src=root,
        url=url_child,
        content=content_child
    )
    assert(not django_backend.news_exists_by(root.owner, root.url))
    assert(not django_backend.news_exists_by(child.owner, child.url))
    django_backend.save_news(child)
    assert(django_backend.news_exists_by(root.owner, root.url))
    assert(django_backend.news_exists_by(child.owner, child.url))


@pytest.mark.django_db
def test_delete_news(django_backend, django_news):
    url = django_news.url
    owner = django_news.schedule.owner

    assert(django_backend.news_exists_by(owner, url))
    django_backend.delete_news(django_news)
    assert(not django_backend.news_exists_by(owner, url))


@pytest.mark.django_db
def test_get_schedule(django_backend, django_schedule):
    assert(
        django_schedule ==
        django_backend.get_schedule(django_schedule.id)
    )


@pytest.mark.django_db
def test_get_schedules(django_backend, django_schedule):
    assert(django_schedule in django_backend.get_schedules())
    assert(django_schedule in django_backend.get_schedules(
        owner=django_schedule.owner
    ))
    assert(django_schedule in django_backend.get_schedules(
        url=django_schedule.url
    ))
    assert(django_schedule in django_backend.get_schedules(
        owner=django_schedule.owner, url=django_schedule.url
    ))
