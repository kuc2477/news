.. news documentation master file, created by
   sphinx-quickstart on Sun Mar  6 17:58:09 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

News
====

News is a schedulable url subscription engine built on top of :mod:`asnycio` and :mod:`aiohttp`. ::

    from celery import Celery
    from django.contrib.auth.models import User

    from news.backends.django import DjangoBackend
    from news.scheduler import Scheduler
    from news.models.django import (
        create_abc_schedule, create_schedule, 
        create_abc_news, create_news
    )

    # define schedule model
    ABCSchedule = create_abc_schedule(user_model=User)
    Schedule = create_schedule(ABCSchedule)

    # define news model
    ABCNews = create_abc_news(schedule_model=Schedule)
    News = create_news(ABCNews)

    # create a celery instance
    celery = Celery()

    # create a schedule backend
    backend = DjangoBackend(
            user_model=User,
            schedule_model=Schedule,
            news_model=News)

    # run news scheduler
    scheduler = Scheduler(backend, celery)
    scheduler.start()


References
----------

.. toctree::
   :maxdepth: 1

   news
   news/reporter
   news/scheduler
   news/cover
   news/backends
   news/backends/django
   news/backends/sqlalchemy
   news/models
   news/models/django
   news/models/sqlalchemy


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

