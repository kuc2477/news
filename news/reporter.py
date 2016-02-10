""":mod: `news.reporter` --- Reporter class for fetching news from the web.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides :class:`~news.reporter.Reporter` class and it's various derivatives.

"""
import itertools
from functools import reduce
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from cached_property import cached_property
from .news import News
from .utils import (
    ext, issuburl, fillurl,
    normalize, depth
)


DEFAULT_FILTER_OPTIONS = {
    'max_dist': None,
    'max_depth': None,
    'blacklist': [],
    'brothers': ['png', 'jpg', 'gif', 'pdf', 'svg', 'zip'],
}


class Reporter(object):

    """Class responsible for fetching :class:`~news.news.News` from the web.

    Provides news fetching interface with various hooks and fetch strategy
    customization points.

    :param url: The url to cover and fetch from the web.
    :type url: :class:`str`
    :param store: The news store backend instance to report news to.
    :type store: Instance of any :class:`news.backends.BackendBase`
        implementations.
    :param predecessor: Predecessor who dispatched the reporter to the url.
        The reporter who has `None` predecessor will be considered as a chief
        reporter, who is be responsible of collecting visited urls and
        managing concurrency.
    :type predecessor: :class:`~news.reporter.Reporter`
    :param report_experience: Lambda function that takes root url of the news
        and a news as arguments and returns `True` if the news is valuable,
        considered valuable, or return `False` otherwise.
    :type report_experience: :func:
    :param fetch_experience: Lambda function that takes root url of the news,
        the news that contains urls and a url as arguments and returns `True`
        if the url is valuable, or return `False` otherwise.
    :type fetch_experience: :func:
    :param dispatch_middlewares: Middlewares to be applied to the reporter's
        `dispatch` method. Provides hooks for logging, news pipelines, etc.
        Each middleware should take `dispatch` method as a parameter and
        return an enhanced `dispatch` method.
    :type dispatch_middlewares: :class:`list`
    :param fetch_middlewares: Middlewares to be applied to the reporter's
        `fetch` method. Provides hooks for logging, news pipelines, etc.
        Each middleware should take `dispatch` method as a parameter and
        return an enhanced `fetch` method.
    :type fetch_middlewares: :class:`list`
    :param filter_options: Link filter options.
    :type filter_options: :class:`dict`

    """
    def __init__(self, url, store, predecessor=None,
                 report_experience=None, fetch_experience=None,
                 dispatch_middlewares=None, fetch_middlewares=None,
                 **filter_options):
        self._url = normalize(url)
        self._store = store
        self._predecessor = predecessor

        self._report_experience = report_experience or (
            lambda root_url, news: True)
        self._fetch_experience = fetch_experience or (
            lambda root_url, news, url: True)

        self._dispatch_middlewares = dispatch_middlewares or []
        self._fetch_middlewares = fetch_middlewares or []
        self._filter_options = DEFAULT_FILTER_OPTIONS.copy()
        self._filter_options = self._filter_options.update(filter_options)

        # enhance `dispatch()` and `fetch()` method with middlewares
        self._enhance_dispatch()
        self._enhance_fetch()

        # create an url mark store to track visited urls if the reporter is
        # the chief reporter.
        if self.is_chief:
            self._visited_urls_lock = asyncio.Lock()
            self._visited_urls = set()

        # reporter summon cache
        self._summon_cache = {}

    async def dispatch(self, bulk_report=False):
        """
        Dispatch the reporter and it's successors to the web to fetch entire
        news tree of the url assigned to him.

        :param bulk_report: Flag that indicates whether the reporter and it's
            successors should report in bulk or not.
        :type bulk_report: :class:`bool`
        :return: List of :class:`~news.news.News` fetched from the url
            assigned to the reporter and it's successors.
        :rtype: :class:`list`

        """
        news = await self.fetch(not bulk_report)
        urls = self._get_worthy_urls(news)

        news_linked = await self.dispatch_successors(urls, bulk_report)
        news_total = news + news_linked

        # Bulk report news if the flag is set to `True`. We don't have to
        # take care of `False` case since it will be reported on `fetch()`
        # calls of each news.
        if bulk_report:
            self._report_news(*news_total)

        return news_total

    async def dispatch_successors(self, urls, bulk_report=False):
        """
        Dispatch the reporter's successors to the web to fetch news subtree of
        the url assigned to him.

        :param bulk_report: Flag that indicates whether the reporter's
            successors should report in bulk or not.
        :type bulk_report: :class:`bool`
        :return: List of :class:`~news.news.News` fetched from the given urls
            by successors of the reporter.
        :rtype: :class:`list`

        """
        successors = self._call_up_successors(urls)
        dispatches = [s.dispatch(bulk_report) for s in successors]
        news_sets = await asyncio.gather(*dispatches)
        news_list = itertools.chain(*news_sets)
        return news_list

    async def fetch(self, immediate_report=True):
        """
        Dispatch the reporter to the web and fetch a news of the url assigned
        to him. Note that the url will be marked as visited whether the
        reporter reported the news or not.

        :param immediate_report: Flag that indicates whether the reporter
            should report the news immediately or not.
        :type immediate_report: :class:`bool`
        :return: :class:`~news.news.News` fetched from the url assigned to the
            reporter.
        :rtype: :class:`~news.news.News`

        """
        async with aiohttp.get(self._url) as response:
            # Notify chief reporter that we visited the url.
            self._report_visited()

            news = News(self._url, await response.text())
            news_valuable = self._worth_report(news)

            # Report the news if the `immediate_report` flag is set to `True`
            # and expected to be valuable based on reporter's experience.
            if immediate_report and news_valuable:
                self._report_news(news)

            # Return the news only if it is valuable based on the reporter's
            # experience.
            return news if news_valuable else None

    def summon_for(self, news):
        """
        Summon the reporter who reported the news.

        Create a reporter responsible for a news stored in backend. This is
        useful when we are to run batch dispatch based on previously fetched
        news tree and need reporters for each corresponding news.

        :param news: The news reported by the reporter to be summoned.
        :type news: :class:`~news.news.News`
        :return: Reporter who reported the news.
        :rtype: :class:`~news.reporter.Reporter`

        """
        # TODO: NOT IMPLEMENTED YET
        pass

    def _enhance_dispatch(self):
        original = self.dispatch
        middlewares = self._dispatch_middlewares
        self.dispatch = reduce(lambda d, m: m(d), middlewares, original)

    def _enhance_fetch(self):
        original = self.fetch
        middlewares = self._fetch_middlewares
        self.fetch = reduce(lambda f, m: m(f), middlewares, original)

    def _report_news(self, *news):
        self._store.add_news(*news)

    def _report_visited(self):
        with (yield from self.chief._visited_urls_lock):
            self.chief._visited_urls.add(self._url)

    def _already_visited(self, url):
        with (yield from self.chief._visited_urls_lock):
            return url in self.chief._visited_urls

    def _get_worthy_urls(self, news):
        atags = BeautifulSoup(news.content, 'html.parser')('a')

        # expand relative / absolute / external urls
        raws = {a['href'] for a in atags if a.has_attr('href')}
        expended = {fillurl(self.chief.url, r) for r in raws}

        # return only worthy urls
        return {e for e in expended if self._worth_visit(news, e)}

    def _worth_report(self, news):
        root = self.chief.url
        return self._report_experience(root, news)

    def _worth_visit(self, news, url):
        root = self.chief.url
        brothers = self._filter_options.get('brothers')
        maxdepth = self._filter_options.get('max_depth')
        maxdist = self._filter_options.get('max_dist')
        blacklist = self._filter_options.get('blacklist')

        is_child = issuburl(root, url)
        is_relative = any([issuburl(b.url, url)] for b in brothers)
        blacklist_ok = ext(url) not in blacklist

        if maxdepth is not None:
            depth_ok = depth(root, url) <= maxdepth
        else:
            depth_ok = True

        if maxdist is not None:
            dist_ok = self.distance_to_chief < maxdist
        else:
            dist_ok = True

        format_ok = (is_child and depth_ok) or is_relative
        expected_valuable = self._fetch_experience(root, news, url)

        return format_ok and dist_ok and blacklist_ok and \
            not self._already_visited(url) and expected_valuable

    def _call_up_successors(self, urls):
        # TODO: NOT IMPLEMENTED YET
        pass

    @cached_property
    def chief(self):
        return self._predecessor.chief if self._predecessor else self

    @cached_property
    def is_chief(self):
        return self.chief == self

    @cached_property
    def distance_to_chief(self):
        return 0 if self.is_chief else self._predecessor.distance_to_chief + 1
