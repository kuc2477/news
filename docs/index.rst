.. news documentation master file, created by
   sphinx-quickstart on Sun Mar  6 17:58:09 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

====
News
====

|build| |coverage|

|logo|

.. |build| image:: https://travis-ci.org/kuc2477/news.svg?branch=dev

.. |coverage| image:: https://coveralls.io/repos/github/kuc2477/news/badge.svg?branch=dev

.. |logo| image:: http://emojipedia-us.s3.amazonaws.com/cache/31/52/3152d71c04eb9dc2082c057e466b35cb.png
    :alt: News, subscription engine built on top of asynchronosy

News is an asynchronous web subscription engine built on top of :mod:`asnycio` and :mod:`aiohttp`. ::

    from celery import Celery
    from django.contrib.auth.models import User
    from news.scheduler import Scheduler
    from news.backends import DjangoBackend
    from news.models.django import (
        create_default_schedule,
        create_default_news,
    )

    # create a celery instance (or use your own instance)
    celery = Celery()

    # define models
    Schedule = create_default_schedule(user_model=User)
    News = create_default_news(schedule_model=Schedule)

    # define a backend
    backend = DjangoBackend(schedule_model=Schedule, news_model=News)

    # subscribe an url
    owner = User.objects.first()
    schedule = Schedule(url='http://httpbin.org', owner=owner)
    schedule.save()

    # run the scheduler
    scheduler = Scheduler(backend, celery)
    scheduler.start()


Quick Start
-----------
.. toctree::
   :maxdepth: 1

   quickstarts/installation
   quickstarts/concepts
   quickstarts/django
   quickstarts/sqlalchemy


User's Guide
------------
.. toctree::
    :maxdepth: 2

    guides/models
    guides/backends
    guides/reporters


API References
---------------

.. toctree::
   :includehidden:
   :maxdepth: 2

   news/models
   news/backends
   news/reporters
   news/scheduler
   news/cover
   news/persister
   news/mapping


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
