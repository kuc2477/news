""":mod:`news.reporters.url` --- URL news reporters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide concrete URL news reporters.

"""
from bs4 import BeautifulSoup
from extraction import Extractor
from ..models import Readable
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
    """URL Reporter for fetching news from plain html web pages"""
    def parse(self, content):
        extractor = Extractor()
        extracted = extractor.extract(content)
        return Readable(url=self.url, title=extracted.title, content=content,
                        summary=extracted.description, image=extracted.image)

    def make_news(self, readable):
        parent = self.parent.fetched_news if not self.is_root else None
        stored = self.backend.get_news_by(owner=self.owner, url=self.url)
        fetched = self.fetched_news

        if not fetched and not stored:
            news = self.backend.News.create_instance(
                parent=parent, schedule=self.schedule,
                **readable.kwargs()
            )
        else:
            news = fetched or stored
            news.parent = parent
            for k, v in readable.kwargs().items():
                setattr(news, k, v)

        return news

    async def get_urls(self, news):
        atags = BeautifulSoup(news.content, 'html.parser')('a')
        links = {a['href'] for a in atags if a.has_attr('href')}
        return {fillurl(self.root.url, l) for l in links}
