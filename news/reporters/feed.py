""":mod:`news.reporters.feed` --- Feed news reporters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide concrete feed news reporters.

"""
import feedparser
from ..models import Readable
from .generics import FeedReporter


class RSSReporter(FeedReporter):
    def parse(self, content):
        f = feedparser.parse(content)
        return (Readable(
            author=e.author, title=e.title, content=e.content, url=e.link,
            summary=e.summary, image=f.image) for e in f.entries)

    def make_news(self, readable):
        return self.backend.News.create_instance(
            schedule=self.schedule, **readable.kwargs())


class AtomReporter(FeedReporter):
    def parse(self, content):
        f = feedparser.parse(content)
        return (Readable(
            author=e.author, title=e.title, content=e.content, url=e.link,
            summary=e.summary, image=f.image) for e in f.entries)

    def make_news(self, readable):
        return self.backend.News.create_instance(
            schedule=self.schedule, **readable.kwargs())
