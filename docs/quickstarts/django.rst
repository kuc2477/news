Quickstart for Django users
===========================
*News* supports *Django* out of the box. Subscribing web contents using *News*
with *Django* is as simple as following.


**1. Define models**

First off, you need to describe how your subscription schedule and web contents
should look like to your database.

.. code-block:: python

   # models.py
   from django.contrib.auth.models import User
   from news.models.django import (
       create_default_news,
       create_default_schedule
   )

   Schedule = create_default_schedule(user_model=User)
   News = create_default_news(schedule_model=Schedule)



**2. Define a backend**

Backend serves as an interface between your models and other :mod:`news`
components. Any backend constructors will produce singleton backend objects
based on combination of supplied models.

.. code-block:: python

   # backend.py
   from news.backends import DjangoBackend
   from .models import Schedule, News

   backend = DjangoBackend(schedule_model=Schedule, news_model=News)


**3. Define a scheduler**

:mod:`news` usese :mod:`celery` as an task queue for distributing cover tasks over
multiple workers. You will need to define your own celery instance and supply
it to the scheduler.

.. code-block:: python

   # celery.py
   from celery import Celery
   celery = Celery()

.. code-block:: python

   # scheduler.py
   from news.scheduler import Scheduler
   from .backend import backend
   from .celery import celery

   scheduler = Scheduler(backend=backend, celery=celery)

   if __name__ == '__main__':
       scheduler.start()


**4. Register the scheduler's celery task**

Celery workers should know what kind of tasks they can work on. Scheduler's
:meth:`make_task` task factory method creates it's news cover task.

.. code-block:: python

   # tasks.py
   from .scheduler import scheduler
   scheduler_task = scheduler.make_task()


**5. Populate your schedules**

To get web contents periodically, you first need to subscribe an url.

.. code-block:: python

   # populate.py
   from django.contrib.auth.models import User
   from .models import Schedule

   if __name__ == '__main__':
       owner = User.objects.first()
       schedule = Schedule(url='http://httpbin.org', owner=owner)
       schedule.save()


**6. Launch celery workers and the scheduler**

Launch celery workers and the scheduler on their each process!

.. code-block:: shell

    $ celery worker
    $ python scheduler.py
