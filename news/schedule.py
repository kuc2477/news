""":mod: `news.schedule` --- News schedules

Provides schedule class which glues all news components(`~news.site.Site`,
`~news.backends`, etc.) togather.

"""
import asyncio
import schedule as worker

from .utils import logger


class Schedule(object):
    """Scraping schedule class

    Represents schedule to be run scraping bounded source sites in every
    predefined cycle.

    :param site: Site to be scheduled for news update.
    :type site: :class:'~news.site.Site'
    :param backend: Backend type to use for page storage.
    :type backend: Any :class:`~news.backend.BackendBase` implementations.
    :param cycle: Cycle for news updates in seconds.
    :type cycle: :class:'int'
    :param loop: Event loop to be used for schedule. Will fall back to
        base asyncio event loop from `asyncio.get_event_loop()` if omitted.
    :type loop: '~asyncio.BaseEventLoop'

    """

    def __init__(self, site, backend, cycle=600, loop=None, **kwargs):
        self.site = site
        self.backend = backend
        self.cycle = cycle
        self.loop = loop or asyncio.get_event_loop()
        self.options = kwargs

    def run(self):
        """Run news updating schedule."""
        # define job
        def job():
            self.run_once(**self.options)

        # set news updating cycle for the job
        worker.every(self.cycle).seconds.do(job)

        # notify logger that we are about to run a schedule
        logger.debug(
            '%s: News schedule with update %d seconds cycle registered' %
            (self.site.url, self.cycle))

        # run schedule
        while True:
            worker.run_pending()

    def run_once(self):
        """Run news update once."""
        logger.debug('%s: News update start' % self.site.url)

        fetch = self.site.fetch_pages(**self.options)
        fetched = self.loop.run_until_complete(fetch)
        new = [p for p in fetched if not self.backend.page_exists(p)]

        # add only new pages to the backend
        self.backend.add_pages(*new)

        logger.debug(
            '%s: News update completed ' % self.site.url +
            '(%d pages fetched / %d pages updated)' % (len(fetched), len(new))
        )
