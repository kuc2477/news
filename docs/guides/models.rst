Models
======
There's 3 type of models in *News*. *User*, *Schedule* and *News*.
Each model describes how user, subscription schedule and news content should be
look like in your own database. Abstract interface of each models are defined
at :mod:`news.models.abstract`. Any models that satisfies those interface's
protocols are sane :mod:`news` model.


Abstract Model Types
---------------------
*News* provides following 3 abstract models for each of models. They can be
concretely defined with factory methods provided by *News*.


User (:class:`~news.models.abstract.AbstractModel`)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*User* describes how a potential owner of `Schedule` should look like.
It's interface defines only 1 unimplemented field
:attr:`~news.models.abstract.AbstractModel.id` which is used to identify
users. Theoratically any persistent models that contain primary key as
*id* column from usual RDBMS are sane candidates of the *User* model.


Schedule (:class:`~news.models.abstract.AbstractSchedule`)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*Schedule*  defines how subscriptions should look like. It contains
:attr:`~news.models.abstract.AbstractSchedule.owner`,
target :attr:`~news.models.abstract.AbstractSchedule.url`,
schedule :attr:`~news.models.abstract.AbstractSchedule.news_type`,
schedule :attr:`~news.models.abstract.AbstractSchedule.cycle`,
reporter :attr:`~news.models.abstract.AbstractSchedule.options` and etc.

You can define your schedule model by using model factory functions from
:mod:`news.models.django` or :mod:`news.models.sqlalchemy` and so on.

.. code-block:: python

    from django.contrib.auth.models import User
    from news.models.django import create_abc_schedule, create_schedule

    ScheduleABC = create_schedule_abc(user_model=User)
    Schedule = create_schedule(ABCSchedule)


News (:class:`~news.models.abstract.AbstractNews`)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
*News*  literally describes your subscribed news content. It contains
:attr:`~news.models.abstract.AbstractNews.schedule`,
:attr:`~news.models.abstract.AbstractNews.title`,
:attr:`~news.models.abstract.AbstractNews.content`,
:attr:`~news.models.abstract.AbstractNews.summary`,
:attr:`~news.models.abstract.AbstractNews.image` and etc.

You can define your news model by using model factory functions from
:mod:`news.models.django` or :mod:`news.models.sqlalchemy` and so on.

.. code-block:: python

    from django.contrib.auth.models import User
    from news.models.django import (
        create_schedule_abc, create_schedule,
        create_news_abc, create_news
    )

    ScheduleABC = create_schedule_abc(user_model=User)
    Schedule = create_schedule(ABCSchedule)

    NewsABC = create_news_abc(schedule_model=Schedule)
    News = create_news(NewsABC)


Extending models
----------------
*News* is designed with extendability in mind. Youc can easily extend default
models via ABC model factory functions. You can extend ABC models from ABC
model factory functions and use them as a source of concrete models with
concrete model factory functions.

.. code-block:: python

    from django.contrib.auth.models import User
    from news.models.django import (
        create_schedule_abc,
        create_news_abc,
        create_schedule,
        create_news
    )

    class ScheduleABC(create_schedule_abc(user_model=User)):
        @property
        def root(self):
            try:
                return [n for n in self.news_list if n.is_root][0]
            except IndexError:
                return None
    Schedule = create_schedule(ScheduleABC)


    class NewsABC(create_news_abc(schedule_model=Schedule)):
        @property
        def tree(self):
            return (self, (n.tree for n in self.children))
    News = create_news(NewsABC)


Persisting schedules
--------------------
As you run your own application, schedules will be created, updated and may
even deleted. It's hard to track those changes since usual
:class:`~news.scheduler.Scheduler` will run on other process than your
application. This is where the :class:`~news.persister.Persister` comes in.
:class:`~news.persister.Persister` persists schedule's states via redis
channel, tracking their update events from model/backend providers(e.g.
Django ORM and SQLAlchemy).

You can easily persist schedules in scheduler process as following:

.. code-block:: python

    # extensions.py
    from redis import Redis
    from news.persister import Persister

    ...

    redis = Redis()
    persister = Persister(redis)


    # models.py
    from django.contrib.auth.models import User
    from news.models.django import create_default_schedule
    from .extensions import persister

    ...

    Schedule = create_default_schedule(user_model=User, persister=persister)


    # scheduler.py
    from news.scheduler import Scheduler
    from .extensions import persister

    ...

    scheduler = Scheduler(backend=backend, celery=celery, persister=persister)
