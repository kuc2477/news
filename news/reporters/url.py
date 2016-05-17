from bs4 import BeautifulSoup
from .generics import TraversingReporter
from .mixins import (
    BatchTraversingMixin,
    DomainTraversingMixin
)
from ..utils.url import fillurl


class URLReporter(
        BatchTraversingMixin,
        DomainTraversingMixin,
        TraversingReporter):
    def parse(self, content):
        return content

    def make_news(self, item):
        src = self.parent.fetched_news if not self.is_root else None
        fetched = self.fetched_news
        stored = self.backend.get_news_by(owner=self.owner, url=self.url)

        if not fetched and not stored:
            return self.backend.News.create_instance(
                self.schedule, self.target, item, src=src
            )
        else:
            news = fetched or stored
            news.content = item
            news.src = src
            return news

    def get_targets(self, news):
        atags = BeautifulSoup(news.content, 'html.parser')('a')
        links = {a['href'] for a in atags if a.has_attr('href')}
        return {fillurl(self.root.target, l) for l in links}

    async def worth_to_visit(self, news, target):
        # TODO: NOT IMPLEMENTED YET
        pass
