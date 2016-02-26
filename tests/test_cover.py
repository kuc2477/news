from news.cover import Cover


def test_cover_factory_method(django_backend, django_news, django_schedule):
    cover = Cover.from_schedule(
        django_schedule, django_backend,
        intel_strategy=(lambda backend: backend.get_news_list(
            owner=django_schedule.owner,
            root_url=django_schedule.url
        ))
    )
    assert(cover.backend == django_backend)
    assert(cover.schedule == django_schedule)
    assert(cover.reporter_meta.schedule == django_schedule)
    assert(django_news in cover.reporter_meta.intel)


def test_cover_prepare(cover):
    assert(cover.reporter is None)
    cover.prepare()
    assert(cover.reporter is not None)
    assert(cover.reporter.meta == cover.reporter_meta)
    assert(cover.reporter.backend == cover.backend)
