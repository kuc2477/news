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
        return Readable(title=extracted.title, content=content,
                        summary=extracted.description, image=extracted.image)

    def make_news(self, readable):
        src = self.parent.fetched_news if not self.is_root else None
        stored = self.backend.get_news_by(owner=self.owner, url=self.url)
        fetched = self.fetched_news

        if not fetched and not stored:
            news = self.backend.News.create_instance(
                url=self.url, schedule=self.schedule, title=readable.title,
                author=readable.author, content=readable.content,
                summary=readable.summary, image=readable.image,
                published=readable.published
            )
        else:
            news = fetched or stored
            news.src = src
            news.author = readable.author
            news.title = readable.title
            news.content = readable.content
            news.summary = readable.summary
            news.image = readable.image
            news.published = readable.published

        return news

    async def get_urls(self, news):
        atags = BeautifulSoup(news.content, 'html.parser')('a')
        links = {a['href'] for a in atags if a.has_attr('href')}
        return {fillurl(self.root.url, l) for l in links}
