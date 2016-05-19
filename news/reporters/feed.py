import feedparser
from . import FeedReporter


class RSSReporter(FeedReporter):
    def parse(self, content):
        f = feedparser.parse(content)
        return (e for e in f.entries)

    def make_news(self, item):
        return self.backend.News.create_instance(
        )


class AtomReporter(FeedReporter):
    def parse(self, content):
        f = feedparser.parse(content)
        return (e for e in f.entries)

    def make_news(self, item):
        return self.backend.News.create_instance(
        )
