from unittest import mock
from django.db.models.signals import (
    post_save,
    post_delete
)
import pytest


@pytest.mark.django_db
def test_get_news(django_backend, django_news):
    url = django_news.url
    owner = django_news.schedule.owner
    assert(django_news == django_backend.get_news(owner, url))
    assert(django_backend.get_news(-1, '') is None)


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

    assert(django_backend.news_exists(owner, url))
    django_backend.delete_news(django_news)
    assert(not django_backend.news_exists(owner, url))


@pytest.mark.django_db
def test_save_news(django_backend, django_schedule, django_news_class,
                   url, content):
    news = django_news_class(
        schedule=django_schedule,
        url=url,
        content=content
    )
    url = news.url
    owner = news.schedule.owner

    assert(not django_backend.news_exists(owner, url))
    django_backend.save_news(news)
    assert(django_backend.news_exists(owner, url))


@pytest.mark.django_db
def test_cascade_save_news(django_backend, django_schedule, django_news_class,
                           url_root, content_root, url_child, content_child):
    root = django_news_class(
        schedule=django_schedule,
        url=url_root,
        content=content_root
    )
    child = django_news_class(
        schedule=django_schedule,
        src=root,
        url=url_child,
        content=content_child
    )
    assert(not django_backend.news_exists(root.owner, root.url))
    assert(not django_backend.news_exists(child.owner, child.url))
    django_backend.save_news(child)
    assert(django_backend.news_exists(root.owner, root.url))
    assert(django_backend.news_exists(child.owner, child.url))


@pytest.mark.django_db
def test_delete_news(django_backend, django_news):
    url = django_news.url
    owner = django_news.schedule.owner

    assert(django_backend.news_exists(owner, url))
    django_backend.delete_news(django_news)
    assert(not django_backend.news_exists(owner, url))


@pytest.mark.django_db
def test_get_schedule(django_backend, django_schedule):
    assert(
        django_schedule ==
        django_backend.get_schedule(django_schedule.owner, django_schedule.url)
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


@pytest.mark.django_db
def test_set_schedule_save_listener_create(
        mocker, django_backend, django_owner, django_schedule_class,
        url):
    stub = mocker.stub()
    django_backend.set_schedule_save_listener(stub)
    schedule = django_schedule_class(url=url, owner=django_owner)
    schedule.save()

    stub.assert_called_once_with(
        instance=schedule,
        sender=django_backend.schedule_class,
        signal=post_save,
        created=True,
        raw=False,
        update_fields=None,
        using='default'
    )

@pytest.mark.django_db
def test_set_schedule_save_listener_update(mocker, django_backend,
                                           django_schedule):
    stub = mocker.stub()
    django_backend.set_schedule_save_listener(stub)
    django_schedule.url = 'changed url'
    django_schedule.save()

    stub.assert_called_once_with(
        instance=django_schedule,
        sender=django_backend.schedule_class,
        signal=post_save,
        created=False,
        raw=False,
        update_fields=None,
        using='default'
    )

@pytest.mark.django_db
def test_set_schedule_delete_listener(mocker, django_backend, django_schedule):
    stub = mocker.stub()
    django_backend.set_schedule_delete_listener(stub)
    django_schedule.delete()

    stub.assert_called_once_with(
        instance=django_schedule,
        sender=django_backend.schedule_class,
        signal=post_delete,
        using='default'
    )
