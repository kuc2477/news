import requests


class Schedule(object):
    """Scraping schedule class

    Represents schedule to be run scraping bounded source sites in every
    predefined cycle.

    """
    def __init__(self, sites, cycle=60):
        """Creates schedule with given sites and cycle"""
        self.sites = sites
        self.cycle = cycle

    def run(self):
        """TODO: Docstring for run.

        :returns: TODO
        """
