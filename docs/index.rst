.. news documentation master file, created by
   sphinx-quickstart on Sun Mar  6 17:58:09 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

News
================

News is a web subscription engine built on top of :mod:`asnycio` and :mod:`aiohttp`. ::

    from celery import Celery
    from django.contrib.auth.models import User
    from news.scheduler import Scheduler
    from news.backends.django import DjangoBackend
    from news.models.django import (
        create_default_schedule,
        create_default_news,
    )

    # define models
    Schedule = create_default_schedule(user_model=User)
    News = create_default_news(schedule_model=Schedule)

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


User's Guide
------------
.. toctree::
   :maxdepth: 2

   guides/django
   guides/sqlalchemy


Advanced Usage
--------------
.. toctree::
    :maxdepth: 2
    advanced/extending_models
    advanced/writing_backends
    advanced/writing_reporters


API References
---------------

.. toctree::
   :maxdepth: 1

   news/scheduler
   news/models
   news/models/django
   news/models/sqlalchemy
   news/backends
   news/backends/django
   news/backends/sqlalchemy
   news/reporters/generics
   news/reporters/mixins
   news/reporters/feed
   news/reporters/url
   news/cover
   news/persister
   news/mapping


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
