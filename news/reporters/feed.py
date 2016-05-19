import feedparser
from . import FeedReporter


class RSSReporter(FeedReporter):
    def parse(self, content):
        f = feedparser.parse(content)
        return (e for e in f.entries)

    def make_news(self, item):
        pass


class AtomReporter(FeedReporter):
    def parse(self, content):
        # TODO: NOT IMPLEMENTED YET
        pass

    def make_news(self, item):
        # TODO: NOT IMPLEMENTED YET
        pass
