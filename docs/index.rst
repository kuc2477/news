.. news documentation master file, created by
   sphinx-quickstart on Sun Mar  6 17:58:09 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

News
====

News is a web subscription engine built on top of :mod:`asnycio` and :mod:`aiohttp`. ::

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
    schedule = Schedule(url='http://www.naver.com', owner=owner, cycle=60)
    schedule.save()

    # run news scheduler
    scheduler = Scheduler(backend, celery)
    scheduler.start()


Installation
------------
You can get the latest version from the PyPI

.. code-block:: shell

    pip install news


Quick Start
-----------
.. toctree::
   :maxdepth: 1

   quickstarts/concepts
   quickstarts/django
   quickstarts/sqlalchemy


User's Guide
------------
.. toctree::
    :maxdepth: 1

    guides/models
    guides/backends
    guides/reporters
    guides/persister
    guides/scheduler


Advanced Usage
--------------
.. toctree::
    :maxdepth: 1

    advanced/extending_models
    advanced/writing_backends
    advanced/writing_reporters
    advanced/middlewares


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
