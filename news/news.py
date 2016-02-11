""":mod:`news.news` --- News domain class and it's functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides :class:`~news.news.News` domain class and it's related utiltiy
functions.

"""
from cached_property import cached_property
from extraction import Extractor

from .domain import DomainBase
from .utils import (
    normalize, depth
)


class News(DomainBase):

    """News domain class

    :param root: Root news of the news.
    :type root: :class:`~news.news.News`
    :param src: Source news of the news.
    :type src: :class:`~news.news.News`
    :param url: URL of the news.
    :type url: :class:`str`
    :param content: Content of the news.
    :type content: :class:`str`

    """

    def __init__(self, root, src, url, content):
        self._root = root
        self._src = src
        self._url = normalize(url)
        self._content = content

    def __str__(self):
        template = '[{0}]: {1}'
        return template.format(self.url, self.title)

    @property
    def id(self):
        template = '{0}:{1}'
        return hash(template.format(self.root.url, self.url))

    @property
    def root(self):
        return self._root

    @property
    def src(self):
        return self._src

    @property
    def url(self):
        return self._url

    @property
    def depth(self):
        return depth(self._root.url, self._url)

    @property
    def distance(self):
        return 0 if self.src is None else self.src.distance + 1

    @cached_property
    def extracted(self):
        extractor = Extractor()
        return extractor.extract(self.content)

    @property
    def title(self):
        return self.extracted.title

    @property
    def image(self):
        return self.extracted.image

    @property
    def description(self):
        return self.extracted.description

    @property
    def content(self):
        return self._content

    @property
    def serialized(self):
        return {
            'root': self.root.url,
            'src': self.src.url,
            'url': self.url,
            'content': self.content,
            'title': self.title,
            'image': self.image,
            'description': self.description
        }
