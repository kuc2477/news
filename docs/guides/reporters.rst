Reporters
=========
*Reporter* is literally a reporter who will be dispatched and discover any
web content news list based on it's assigned *Scehdule*. It is one of the
core *News* components and it is responsible for fetching, parsing and
pipelining web contents.


Middlewares
-----------
Reporters can be enhanced by two type of middlewares. ``dispatch_middleware`` and
``fetch_middleware``. Middlewares are essentially a function descorators for
:meth:`~news.reporters.abstract.Reporter.dispatch` and
:meth:`~news.reporters.abstract.Reporter.fetch`. Any functions that satisfy
following protocols are sane reporter middlewares.

- ``dispatch_middleware``: A function that takes an 
  :class:`~news.reporters.abstract.Reporter` and
  :meth:`~news.reporters.abstract.Reporter.dispatch` method and
  returns enhanced :meth:`~news.reporters.abstract.Reporter.dispatch`.


- ``fetch_middleware``: A function that takes an
  :class:`~news.reporters.abstract.Reporter` and
  :meth:`~news.reporters.abstract.Reporter.fetch` method and
  returns enhanced :meth:`~news.reporters.abstract.Reporter.fetch`.


Reporter middlewares especially comes handy when useful when you are building 
news pipeline or callback chains.


Generic reporters
-----------------
Generic reporters are generic base reporters which are subclasses of 
:class:`~news.reporters.abstract.Reporter`. They provide generic implementation
of :meth:`~news.reporter.abstract.Reporter.dispatch` and other additional
mechanism of news discovery if necessary. *News* currently provides 2 types
of generic reporters: :class:`~news.reporters.generics.TraversingReporter` and
:class:`~news.reporters.generics.FeedReporter`. 
:class:`~news.reporters.generics.TraversingReporter` implements generic
mechanism of traversing along a tree of news contents. 
:class:`~news.reporters.generics.FeedReporter`, on the other hand, provides
generic mechanism of discovering news contents from a static feed url.



Extending reporters
-------------------
You can easily extend generic reporters from :mod:`news.reporters.generics` or
from :mod:`news.reporter.abstract` to build your own reporter from the very
scratch. Any :class:`~news.reporters.abstract.Reporter` subclasses that satisfies
it's :meth:`~news.reporters.abstract.Reporter.dispatch`,
:meth:`~news.reporters.abstract.Reporter.parse` and
:meth:`~news.reporters.abstract.Reporter.make_news` protocls are sane
reporters.

**Example** ::

    from bs4 import BeautifulSoup
    from news.models.abstract import Readable
    from news.reporters.generics import TraversingReporter


    class ReditThreadReporter(TraversingReporter):
        def __init__(thread=None, *args, **kwargs):
            self.__init__(*args, **kwargs)
            self.thread = thread or 'all'

        def parse(content):
            return Readable(title= ...)

        def make_news(readable):
            return self.backend.News.create_instance(
                parent=self.parent.fetched_news, ...
                **readable.kwargs()
            )

        def get_urls(self, news):
            soup = BeautifulSoup(content)
            return (a['href'] for a in soup['a'] if self.thread in a['href'])



Mapping from schedules to reporters
-----------------------------------
To use your own customized/extended reporters, you need a mapping mechanism for
mapping from a schedule to a specific reporter. :class:`~news.mapping.Mapping`
exactly does that mapping.

**Example**

.. code-block:: python

    from news.mapping import Mapping
    from .reporters import ReditThreadReporter
    from .scheduler import scheduler

    mapping = Mapping({
        'redit': lambda schedule: return {
            'thread': schedule.options['thread']
        }
    })

    scheduler.configure(mapping=mapping)
    scheduler.start()
