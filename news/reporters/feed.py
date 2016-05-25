""":mod:`news.reporters.feed` --- Feed reporters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide concrete feed news reporters.

"""
import feedparser
from ..models.abstract import Readable
from .generics import FeedReporter


class RSSReporter(FeedReporter):
    """RSS Reporter for fetching RSS feeds.

    :param meta: Reporter meta from which to populate the reporter.
    :type meta: :class:`news.reporters.ReporterMeta`
    :param backend: Backend to report news.
    :type backend: :class:`news.backends.abstract.AbstractBackend`

    """
    def parse(self, content):
        """Parses feed content of http response body into multiple
        :class:`news.models.abstract.Readable`s.

        Internally uses :mod:`~feedparser` library to extract entries from the
        response body.

        :param content: Http response body
        :type content: :class:`str`
        :returns: An iterator of parsed readables
        :rtype: An iterator of :class:`news.models.abstract.Readable`

        """
        f = feedparser.parse(content)
        return (Readable(
            author=e.author, title=e.title, content=e.content, url=e.link,
            summary=e.summary, image=f.image) for e in f.entries)

    def make_news(self, readable):
        """Instantiate a news out of the readable parsed from :meth:`parse`.

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
    def parse(self, content):
        """Parses feed content of http response body into multiple
        :class:`news.models.abstract.Readable`s.

        Internally uses :mod:`~feedparser` library to extract entries from the
        response body.

        :param content: Http response body
        :type content: :class:`str`
        :returns: An iterator of parsed readables
        :rtype: An iterator of :class:`news.models.abstract.Readable`

        """
        f = feedparser.parse(content)
        return (Readable(
            author=e.author, title=e.title, content=e.content, url=e.link,
            summary=e.summary, image=f.image) for e in f.entries)

    def make_news(self, readable):
        """Instantiate a news out of the readable parsed from :meth:`parse`.

        :param readable: A parsed readable.
        :type readable: :class:`news.model.abstract.Readable`
        :returns: A news instance
        :rtype: :class:`news.models.abstract.AbstractNews` implementation

        """
        return self.backend.News.create_instance(
            schedule=self.schedule, **readable.kwargs())
