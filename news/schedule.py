import asyncio
import schedule as worker


class Schedule(object):
    """Scraping schedule class

    Represents schedule to be run scraping bounded source sites in every
    predefined cycle term.

    """
    def __init__(self, site, term=60, loop=None):
        """Creates schedule with given sites and cycle"""
        self.site = site
        self.term = term
        self.loop = loop or asyncio.get_event_loop()


    def run(self):
        """Run site news scrapper schedule."""
        def job():
            self.loop.run_until_complete(self.site.update_pages())

        worker.every(self.term).minutes.do(job)

        while True:
            worker.run_pending()
