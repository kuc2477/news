""":mod:`news.reporters.feed` --- Feed reporters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide concrete feed news reporters.

"""
from .generics import FeedReporter


class RSSReporter(FeedReporter):
    """RSS Reporter for fetching RSS feeds.

    :param meta: Reporter meta from which to populate the reporter.
    :type meta: :class:`news.reporters.ReporterMeta`
    :param backend: Backend to report news.
    :type backend: :class:`news.backends.abstract.AbstractBackend`

    """
    parser = 'news.parsers.parse_rss'

    def make_news(self, readable):
        """Instantiate a news out of the readable parsed from :attr:`parser`.

        :param readable: A parsed readable.
        :type readable: :class:`news.model.abstract.Readable`
        :returns: A news instance
        :rtype: :class:`news.models.abstract.AbstractNews` implementation

        """
        return self.backend.News.create_instance(
            schedule=self.schedule, **readable.kwargs())


class AtomReporter(FeedReporter):
    """Atom Reporter for fetching Atom feeds.

    :param meta: Reporter meta from which to populate the reporter.
    :type meta: :class:`news.reporters.ReporterMeta`
    :param backend: Backend to report news.
    :type backend: :class:`news.backends.abstract.AbstractBackend`

    """
    parser = 'news.parsers.parse_atom'

    def make_news(self, readable):
        """Instantiate a news out of the readable parsed from :attr:`parser`.

        :param readable: A parsed readable.
        :type readable: :class:`news.model.abstract.Readable`
        :returns: A news instance
        :rtype: :class:`news.models.abstract.AbstractNews` implementation

        """
        return self.backend.News.create_instance(
            schedule=self.schedule, **readable.kwargs())
