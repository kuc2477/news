""":mod: `news.schedule` --- News schedules

Provides schedule class which glues all news components(`~news.site.Site`,
`~news.backends`, etc.) togather.

"""
import asyncio
import schedule as worker


class Schedule(object):
    """Scraping schedule class

    Represents schedule to be run scraping bounded source sites in every
    predefined cycle term.

    :param site: Site to be scheduled for news update.
    :type site: :class:'news.site.Site'
    :param term: Cycle term for news updates in seconds.
    :type term: :class:'int'
    :param loop: Event loop to be used for schedule. Will fall back to
        base asyncio event loop from `asyncio.get_event_loop()` if omitted.
    :type loop: '~asyncio.BaseEventLoop'

    """

    def __init__(self, site, term=600, loop=None):
        self.site = site
        self.term = term
        self.loop = loop or asyncio.get_event_loop()


    def run(self):
        """Run news updating schedule."""
        # define news updating job
        def job():
            self.loop.run_until_complete(self.site.update_pages())

        # set news updating cycle term for the job
        worker.every(self.term).seconds.do(job)

        # run schedule
        while True:
            worker.run_pending()
