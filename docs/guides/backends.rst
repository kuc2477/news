Backends
========
*Backend* serves as an interface between your models and the rest of *News* components.
*News* currently supports *Django* and *SQLAlchemy* backends out of the box.
:class:`~news.backends.abstract.AbstractBackend` describes common interface
that all concrete backends should satisfy.

.. code-block:: python

   from news.backends import DjangoBackend
   from .models import Schedule, News

   backend = DjangoBackend(schedule_model=Schedule, news_model=News)


Writing your own backends
-------------------------
Any backend implementation that satisfies `~news.backends.abstract.AbstractBackend`
protocols are sane backends. Note that you must implement backend's models 
accordingly too.
