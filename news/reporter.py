""":mod: `news.reporter` --- Reporter class for fetching news from the web.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides :class:`~news.reporter.Reporter` class and it's various derivatives.

"""
import copy
import itertools
from functools import reduce
from bs4 import BeautifulSoup
import asyncio
import aiohttp
from cached_property import cached_property
from .news import News
from .constants import DEFAULT_FILTER_OPTIONS
from .utils import (
    ext, issuburl, fillurl,
    normalize, depth
)


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

        # news will be set on reporter once fetched
        self._news = None

        # enhance `dispatch()` and `fetch()` method with middlewares
        self._enhance_dispatch()
        self._enhance_fetch()

        # create an url mark store to track visited urls if the reporter is
        # the chief reporter.
        if self.is_chief:
            self._visited_urls_lock = asyncio.Lock()
            self._visited_urls = set()

    @classmethod
    def create_chief_reporter(
            cls, url, store, intelligence=None,
            report_experience=None, fetch_experience=None,
            dispatch_middlewares=None, fetch_middlewares=None,
            **filter_options):
        chief = cls(
            url, store,
            intelligence=intelligence, predecessor=None,
            report_experience=report_experience,
            fetch_experience=fetch_experience,
            dispatch_middlewares=dispatch_middlewares,
            fetch_middlewares=fetch_middlewares,
            **filter_options
        )
        return chief

    @property
    def fetched_news(self):
        return self._news

    @fetched_news.setter
    def fetched_news(self, news):
        self._news = news

    @property
    def hash_fetched(self):
        return self._news is not None

    @property
    def url(self):
        return self._url

    @property
    def predecessor(self):
        return self._predecessor

    @cached_property
    def chief(self):
        return self._predecessor.chief if self._predecessor else self

    @cached_property
    def is_chief(self):
        return self.chief == self

    @cached_property
    def chief_url(self):
        return self.chief._url

    @cached_property
    def distance_to_chief(self):
        return 0 if self.is_chief else self._predecessor.distance_to_chief + 1

    async def dispatch(self, intelligence=None, bulk_report=False):
        """
        Dispatch the reporter and it's successors to the web to fetch entire
        news tree of the url assigned to him.

        :param intelligence: A list of news that was fetched in the past.
            Reporters responsible for each news of intelligence will be
            summoned by the reporter and dispatched along with the reporters
            recruited for the urls of the fetched news. This can work as a
            performance boost since reporters summoned for each news of
            intelligence can be dispatched without wating for their
            predecessors to dispatch them.
        :type intelligence: :class:`list`
        :param bulk_report: Flag that indicates whether the reporter and it's
            successors should report in bulk or not.
        :type bulk_report: :class:`bool`
        :return: List of :class:`~news.news.News` fetched from the url
            assigned to the reporter and it's successors.
        :rtype: :class:`list`

        """
        news = await self.fetch(not bulk_report)
        urls = self._get_worthy_urls(news)

        news_linked = await self.dispatch_reporters(
            urls, intelligence, bulk_report)

        news_total = news_linked.append(news)

        # Bulk report news if the flag is set to `True`. We don't have to
        # take care of `False` case since it will be reported on `fetch()`
        # calls of each news.
        if bulk_report:
            self._report_news(*news_total)

        return news_total

    async def dispatch_reporters(self, urls,
                                 intelligence=None,
                                 bulk_report=False):
        """
        Dispatch the reporter's successors to the web to fetch news subtree of
        the url assigned to him.

        :param urls: A list of urls to recruit reporters and dispatch them.
        :type urls: :class:`list`
        :param intelligence: A list of news that was fetched in the past.
            Reporters responsible for each news of intelligence will be
            summoned by the reporter and dispatched along with the reporters
            recruited for the urls. This can work as a performance boost since
            reporters summoned for each news of intelligence can be dispatched
            without wating for their predecessors to dispatch them.
        :type intelligence: :class:`list`
        :param bulk_report: Flag that indicates whether the reporter's
            successors should report in bulk or not.
        :type bulk_report: :class:`bool`
        :return: List of :class:`~news.news.News` fetched from the given urls
            by successors of the reporter.
        :rtype: :class:`list`

        """
        # recruite new reporters for urls and summon reporters responsible
        # for each news intelligence.
        recruited = self._recruit_reporters(urls)
        summoned = self._summon_reporters(intelligence) if \
            self.is_chief else []

        reporters = recruited + summoned

        dispatches = [r.dispatch(bulk_report=bulk_report) for r in reporters]
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
        async with aiohttp.get(self.url) as response:
            # report to the chief reporter that we visited the url.
            self._report_visited()

            # refine response into a news
            root = self.chief.fetched_news
            src = self.predecessor.fetched_news if self.predecessor else None
            news = News(root, src, self.url, await response.text())

            # set fetched news to the reporter.
            self.fetched_news = news

            # determine whether the news is worth to report or not
            worth_to_report = self._worth_report(news)

            # Report the news if the `immediate_report` flag is set to `True`
            # and expected to be valuable based on reporter's experience.
            if immediate_report and worth_to_report:
                self._report_news(news)

            # Return the news only if it is valuable based on the reporter's
            # experience.
            return news if worth_to_report else None

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
        return self._report_experience(self.chief_url, news)

    def _worth_visit(self, news, url):
        brothers = self._filter_options.get('brothers')
        maxdepth = self._filter_options.get('max_depth')
        maxdist = self._filter_options.get('max_dist')
        blacklist = self._filter_options.get('blacklist')

        is_child = issuburl(self.chief_url, url)
        is_relative = any([issuburl(b.url, url)] for b in brothers)
        blacklist_ok = ext(url) not in blacklist

        if maxdepth is not None:
            depth_ok = depth(self.chief_url, url) <= maxdepth
        else:
            depth_ok = True

        if maxdist is not None:
            dist_ok = self.distance_to_chief < maxdist
        else:
            dist_ok = True

        format_ok = (is_child and depth_ok) or is_relative
        expected_valuable = self._fetch_experience(self.chief_url, news, url)

        return format_ok and dist_ok and blacklist_ok and \
            not self._already_visited(url) and expected_valuable

    def _take_responsibility(self, news):
        if news.src:
            predecessor = copy.deepcopy(self)
            predecessor._take_responsibility(news.src)
        else:
            predecessor = self.chief

        self._url = news.url
        self._predecessor = predecessor
        self.fetched_news = news

    def _summon_for(self, news):
        reporter = copy.deepcopy(self)
        reporter._take_responsibility(news)
        return reporter

    def _summon_reporters(self, news_list):
        # summon reporters only that has same root url with our chief
        # reporter's url.
        return [self._summon_for(n) for n in news_list if
                n.root.url == self.chief_url]

    def _recruit_for(self, url):
        reporter = copy.deepcopy(self)
        reporter._url = url
        reporter._predecessor = self
        return reporter

    def _recruit_reporters(self, urls):
        return [self._recruit_for(u) for u in urls]
