.. news documentation master file, created by
   sphinx-quickstart on Sun Mar  6 17:58:09 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

News
====

News is a schedulable url subscription engine based on :mod:`asnycio`. ::

    from celery import Celery
    from django.contrib.auth.models import User
    from news.backends.django import DjangoBackend
    from news.scheduler import Scheduler
    from news.models.django import Schedule, News

    # create a url subscription schedule
    owner = User.objects.first()
    Schedule.objects.create(owner=owner, url='http://httpbin.org')

    # create a news backend
    celery = Celery()
    backend = DjangoBackend(
            user_class=User,
            schedule_class=Schedule,
            news_class=News
        )

    # run news scheduler
    scheduler = Scheduler(backend, celery)
    scheduler.start()


References
----------

.. toctree::
   :maxdepth: 2

   news
   news/reporter
   news/scheduler
   news/cover
   news/backends/abstract
   news/backends/django
   news/backends/sqlalchemy
   news/models/abstract
   news/models/django
   news/models/sqlalchemy


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

