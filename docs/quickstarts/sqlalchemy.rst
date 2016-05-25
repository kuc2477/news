Quickstart for SQLAlchemy users
===============================
*News* supports *SQLAlchemy* out of the box. Subscribing web contents using
*News* with *SQLAlchemy* is as simple as following.


1. Define news models

   .. code-block:: python

       # models.py
       from sqlalchemy import Column, Integer
       from sqlalchemy.ext.declarative import declarative_base
       from news.models.sqlalchemy import (
           create_default_news,
           create_default_schedule
       )

       base = declarative_base()

       class User(base):
            __tablename__ = 'user'
           id = Column(Integer, primary_key=True)

       Schedule = create_default_schedule(user_model=User, base=base)
       News = create_default_news(schedule_model=Schedule, base=base)



2. Create a news backend

   .. code-block:: python

       # backend.py
       from news.backends import SQLAlchemyBackend
       from .models import Schedule, News

       backend = SQLAlchemyBackend(schedule_model=Schedule, news_model=News)


3. Create a celery app instance and register the scheduler's celery task

   .. code-block:: python

       # celery.py
       from celery import Celery
       celery = Celery()


  .. code-block:: python

       # tasks.py
       from .scheduler import scheduler
       scheduler_task = scheduler.make_task()


4. Define a scheduler

   .. code-block:: python

       # scheduler.py
       from news.scheduler import Scheduler
       from .backend import backend
       from .celery import celery

       scheduler = Scheduler(backend=backend, celery=celery)

       if __name__ == '__main__':
           scheduler.start()


5. Populate your news schedules

   .. code-block:: python

       # populate.py
       from .models import User, Schedule
       from .extensions import session

       if __name__ == '__main__':
           owner = User.query.first()
           schedule = Schedule(url='http://httpbin.org', owner=owner)
           session.add(schedule)
           session.commit()


6. Launch your celery process against ``tasks.py``


7. Launch your scheduler process with ``python scheduler.py``
