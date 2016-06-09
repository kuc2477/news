""":mod:`news.parsers` --- Default parser implementations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide default parser implementations.

Parsers are basically pure functions that returns
(:class:`~news.models.abstract.Readable`)(s) given an (:class:`str`)url and
a (:class:`str`)content passed from a
(:class:`~news.reporters.abstract.Reporter`).

"""
import feedparser
from extraction import Extractor
from ..models.abstract import Readable


def parse_html(url, content):
    """Parses HTML content of http response body into a single
    :class:`~news.models.abstract.Readable`.

    Internally uses :class:`~extraction.Extractor` extractor to extract
    sementic tags from the plain html content.

    :param url: URL of the content.
    :type url: :class:`str`
    :param content: Http response body
    :type content: :class:`str`
    :returns: A parsed readable
    :rtype: :class:`~news.models.abstract.Readable`

    """
    extractor = Extractor()
    extracted = extractor.extract(content)
    return Readable(url=url, title=extracted.title, content=content,
                    summary=extracted.description, image=extracted.image)


def parse_rss(url, content):
    """Parses RSS content of http response body into
    :class:`~news.models.abstract.Readable`s.

    Internally uses :class:`~extraction.Extractor` extractor to extract
    sementic tags from the plain html content.

    :param url: URL of the content.
    :type url: :class:`str`
    :param content: Http response body
    :type content: :class:`str`
    :returns: A parsed readable
    :rtype: :class:`~news.models.abstract.Readable`

    """
    f = feedparser.parse(content)
    return (Readable(
        author=e.author, title=e.title, content=e.content, url=e.link,
        summary=e.summary, image=f.image) for e in f.entries)


def parse_atom(url, content):
    """Parses ATOM content of http response body into a single
    :class:`~news.models.abstract.Readable`s.

    Internally uses :class:`~extraction.Extractor` extractor to extract
    sementic tags from the plain html content.

    :param url: URL of the content.
    :type url: :class:`str`
    :param content: Http response body
    :type content: :class:`str`
    :returns: A parsed readable
    :rtype: :class:`~news.models.abstract.Readable`

    """
    f = feedparser.parse(content)
    return (Readable(
        author=e.author, title=e.title, content=e.content, url=e.link,
        summary=e.summary, image=f.image) for e in f.entries)
