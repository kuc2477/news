""":mod:`news.reporters.feed` --- Feed news reporters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide concrete feed news reporters.

"""
import feedparser
from .generics import FeedReporter


class RSSReporter(FeedReporter):
    def parse(self, content):
        f = feedparser.parse(content)
        return (e for e in f.entries)

    def make_news(self, item):
        # TODO: NOT IMPLEMENTED YET
        return self.backend.News.create_instance(
        )


class AtomReporter(FeedReporter):
    def parse(self, content):
        f = feedparser.parse(content)
        return (e for e in f.entries)

    def make_news(self, item):
        # TODO: NOT IMPLEMENTED YET
        return self.backend.News.create_instance(
        )
