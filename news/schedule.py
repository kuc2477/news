""":mod: `news.schedule` --- News schedules

Provides schedule class which glues all news components(`~news.site.Site`,
`~news.backends`, etc.) together.

"""
from itertools import product

import asyncio
import schedule as worker

from .utils import elapsed_timer
from .utils import logger


class Schedule(object):
    """Scraping schedule class

    Represents schedule to be run scraping bound source site in every
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
    :param fetch_callbacks: Callbacks to be fired when pages are fetched.
    :type fetch_callbacks: :class:`list`
    :param add_callbacks: Callbacks to be fired when pages are added.
    :type add_callbacks: :class:`list`
    :param pipes: Pipeline functions that filters fetched pages
    :type pipes: :class:`list`
    :param on_start: Callback to be fired on schedule job start.
    :type on_start: :class:`function`
    :param on_complete: Callback to be fired on schedule job finish.
    :type on_complete: :class:`function`
    :param **kwargs: Fetch options for `~news.page.Page.fetch_linked_pages`
    :type **kwargs: :class:`dict`

    """

    def __init__(self, site, backend, cycle=600, loop=None,
                 fetch_callbacks=[], add_callbacks=[], pipes=[],
                 on_start=None, on_complete=None, **kwargs):
        self.site = site
        self.backend = backend
        self.cycle = cycle
        self.loop = loop or asyncio.get_event_loop()

        self.fetch_callbacks = fetch_callbacks
        self.update_callbacks = add_callbacks
        self.pipes = pipes
        self.on_start = on_start
        self.on_complete = on_complete

        self.options = kwargs

    def run(self):
        """Run news updating schedule."""
        # set news updating cycle for the job
        worker.every(self.cycle).seconds.do(lambda: self.run_once())

        # notify logger that we are about to run a schedule
        logger.debug(
            '%s: News schedule registered with cycle of %d seconds' %
            (self.site.url, self.cycle))

        # run schedule
        while True:
            worker.run_pending()

    def run_once(self):
        """Run news update once."""
        logger.debug('%s: News update start' % self.site.url)

        # fire start callback if exists
        if self.on_start:
            self.on_start(self)

        with elapsed_timer() as elapsed:
            fetch = self.site.fetch_pages(**self.options)
            fetched = self.loop.run_until_complete(fetch)

            # apply pipelines
            for pipe in self.pipes:
                fetched = pipe(fetched)

            # fire fetch callbacks
            for page, callback in product(fetched, self.fetch_callbacks):
                callback(page)

            # filter out pages that already exists in the store
            new = [p for p in fetched if not self.backend.page_exists(p)]

        # add new pages to the backend
        self.backend.add_pages(*new)

        # fire add callbacks
        for page, callback in product(new, self.update_callbacks):
            callback(page)

        # show logs
        template = '{site}: News update completed in {elapsed:.2f} seconds '
        template += '({fetched} fetched / {added} added)'
        logger.debug(template.format(
            site=self.site.url, elapsed=elapsed(),
            fetched=len(fetched), added=len(new)
        ))

        # fire complete callback if exists
        if self.on_complete:
            self.on_complete(self)
