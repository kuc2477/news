Basic conecpts
==============
News is basically an asynchronous web content (e.g. HTML, RSS or Atom)
subscription engine which consists of 4 major components: ``Model``, ``Backend``,
``Scheduler`` and ``Reporter``.


Model
-----
``Model`` represents your subscription schedules and fetched web contents which
will be persisted in your own database. *News* currently supports *Django* and
*SQLAlchemy* models out of the box.


Backend
-------
``Backend`` serves as an interface between your models and rest of *News* components,
for example, ``Scheduler`` or ``Reporter``. *News* currently supports *Django* and
*SQLAlchemy* backends out of the box.


Reporter
--------
``Reporter`` is literally a reporter who will be dispatched and discover any
web content news based on it's assigned ``Schedule`` . *News* provides ``URLReporter``,
``RSSReporter`` and ``AtomReporter`` out of the box. You can easily write or extend
your own reporters by subclassing genric reporters such as ``TraversingReporter`` or
``FeedReporter`` too.


Scheduler
---------
``Scheduler`` is a main component that will schedule your subscriptions and
dispatch ``Reporter`` on each of their reserved time. It can also be persisted
between processes or threads via redis-powered ``Persister`` component. Usually
``Scheduler`` should run on it's own process.
