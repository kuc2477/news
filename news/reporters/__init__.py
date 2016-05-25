""":mod:`news.reporters` --- News reporters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides :class:`ReporterMeta` which can be used to populate reporters from
a schedule.

"""
from .feed import AtomReporter, RSSReporter
from .url import URLReporter


class ReporterMeta(object):
    """Reporter's meta information.

    Abstracts a schedule as a meta information of a reporter and provide means
    to access the schedule from the reporters.

    :param schedule: Schedule that will be assigned to the reporter.
    :type schedule: :class:`news.models.abstract.AbstractSchedule`
        implementation

    """
    def __init__(self, schedule):
        self._schedule = schedule

    @property
    def schedule(self):
        return self._schedule

    @property
    def owner(self):
        """(:class:`~news.models.AbstractSchedule` implemntation) Owner of the
        reporter's schedule."""
        return self.schedule.owner

    @property
    def options(self):
        """(:class:`dict`) Reporter options."""
        return self.schedule.options
