""":mod: `news.reporter` --- Contains reporter related classes.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides :class:`~news.reporter.Reporter` class and it's derivatives.

"""
from functools import reduce
import copy
import itertools
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from cached_property import cached_property
from .utils.url import (
    ext, issuburl, fillurl,
    normalize, depth
)


__all__ = ['ReporterMeta', 'Reporter']


class ReporterMeta(object):
    """
    Meta information / options to be used by reporters.

    :param schedule: Schedule which created the chief reporter of the
        reporter or reporter itself. Schedule provides necessary information
        such as the owner of the schedule or filter options to use in news
        fetching process.
    :type schedule: Implementation of `~news.models.AbstractSchedule`.
    :param intel: A list of news that was fetched in the past.
        Reporters responsible for each news of intel will be
        summoned by the reporter and dispatched along with the reporters
        recruited for the urls of the fetched news. This can work as a
        performance boost since reporters summoned for each news of
        intel can be dispatched without wating for their
        predecessors to dispatch them.
    :type intel: :class:`list`
    :param report_experience: Lambda function that takes schedule of the news
        and a news as arguments and returns `True` if the news is valuable,
        considered valuable, or return `False` otherwise.
    :type report_experience: :func:
    :param fetch_experience: Lambda function that takes schedule of the news
        and a news that contains urls and a url as arguments and returns
        `True` if the url is valuable, or return `False` otherwise.
    :type fetch_experience: :func:

    """
    def __init__(self, schedule, intel=None,
                 report_experience=None,
                 fetch_experience=None,):
        # Schedule meta that contains information about owner and
        # filter options.
        self.schedule = schedule

        # Intel (list of news) to be used for batch-fetching, which will
        # impreove performance of the chief reporter's initial fetch.
        self.intel = intel or []

        # Experience of the reporter, which will filter out meaningless
        # urls or news, thus improve performance of the reporter.
        self.report_experience = report_experience or (
            lambda schedule, news: True
        )
        self.fetch_experience = fetch_experience or (
            lambda schedule, news, url: True
        )

    @property
    def owner(self):
        """
        (`~news.models.AbstractOwnerMixin` implementation of
        :attr:`schedule` backend type) The owner of the schedule meta that
        is used to instantiate this reporter meta.

        """

        return self.schedule.owner

    @property
    def filter_options(self):
        """
        (:class:`dict`) Filter options to be used by reporters.

        """
        return self.schedule.get_filter_options()


class Reporter(object):
    """
    Reporter responsible for fetching a list of news under given url.

    :param url: The url to cover and fetch from the web.
    :type url: :class:`str`
    :param meta: Meta information to be used in fetching process.
    :type meta: :class:`~news.reporter.ReporterMeta`
    :param backend: The news store backend instance to report news to.
    :type backend: Instance of any :class:`news.backends.BackendBase`
    :param predecessor: Predecessor who dispatched the reporter to the url.
        The reporter who has `None` predecessor will be considered as a chief
        reporter, who is be responsible of collecting visited urls and
        managing concurrency.
    :type predecessor: :class:`~news.reporter.Reporter`

    """

    def __init__(self, url, meta, backend, predecessor=None):
        self.url = normalize(url)
        self.meta = meta
        self.backend = backend
        self.predecessor = predecessor

        # news will be set on reporter once fetched
        self._news = None

        # create an url mark store to track visited urls if the reporter is
        # the chief reporter.
        if self.is_chief:
            self._visited_urls_lock = asyncio.Lock()
            self._visited_urls = set()

    # ============================
    # Fetched news getter / setter
    # ============================

    @property
    def fetched_news(self):
        return self._news

    @fetched_news.setter
    def fetched_news(self, news):
        self._news = news

    # =============
    # Reporter meta
    # =============

    @property
    def schedule(self):
        return self.meta.schedule

    @property
    def owner(self):
        return self.meta.owner

    @property
    def filter_options(self):
        return self.meta.filter_options

    # =====================
    # Reporter relationship
    # =====================

    @cached_property
    def chief(self):
        return self.predecessor.chief if self.predecessor else self

    @cached_property
    def is_chief(self):
        return self.chief == self

    @cached_property
    def distance(self):
        return 0 if not self.predecessor else self.predecessor.distance + 1

    # =================
    # Reporter dispatch
    # =================

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
        urls = await self.get_worthy_urls(news) if news else []

        news_linked = await self.dispatch_reporters(urls, bulk_report)
        news_total = news_linked.append(news)

        # Bulk report news if the flag is set to `True`. We don't have to
        # take care of `False` case since news should be reported on `fetch()`
        # calls of each successors already.
        if bulk_report and self.is_chief:
            self.report_news(*news_total)

        return news_total

    async def dispatch_reporters(self, urls, bulk_report=False):
        """
        Dispatch the reporter's successors to the web to fetch news subtree of
        the url assigned to him.

        :param urls: A list of urls to recruit reporters and dispatch them.
        :type urls: :class:`list`
        :param bulk_report: Flag that indicates whether the reporter's
            successors should report in bulk or not.
        :type bulk_report: :class:`bool`
        :return: List of :class:`~news.news.News` fetched from the given urls
            by successors of the reporter.
        :rtype: :class:`list`

        """
        reporters = self.call_up_reporters(urls)
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
            await self.report_visited()

            # make news from response and set fetched
            self.fetched_news = news = self.make_news(await response.text())

            if not self.worth_to_report(news):
                return None

            if immediate_report:
                self.report_news(news)

            return news

    # ====
    # News
    # ====

    def make_news(self, content):
        src = self.predecessor.fetched_news if not self.chief else None
        news_class = self.backend.news_class
        news = news_class.create_instance(
            self.schedule, self.url, content, src=src)
        return news

    # =========
    # Enhancers
    # =========

    def enhance_dispatch(self, *middlewares):
        """
        Enhance dispatch method of the reporter with middlewares.

        :param middlewares: Middlewares to be applied to the reporter's
            `dispatch` method. Provides hooks for logging, news pipelines, etc.
            Each middleware should take reporter itself and the `dispatch`
            method as arguements and return an enhanced `dispatch` method.
        :type middlewares: Arbitrary number of middlewares.

        """
        if not hasattr(self, '_original_dispatch'):
            self._original_dispatch = self.dispatch

        self.dispatch = reduce(lambda d, m: m(self, d), middlewares,
                               self.dispatch)

    def enhance_fetch(self, *middlewares):
        """
        Enhance fetch method of the reporter with middlewares.

        Unlike dispatch middlewares, enhanced fetch method will be inherited
        to successor reporters too.

        :param middlewares: Middlewares to be applied to the reporter's
            `fetch` method. Provides hooks for logging, news pipelines, etc.
            Each middleware should take reporter itself and the `dispatch`
            method as arguments and return an enhanced `fetch` method.
        :type middlewares: Arbitrary number of middlewares.

        """
        if not hasattr(self, '_original_fetch'):
            self._original_fetch = self.fetch

        self.fetch = reduce(lambda f, m: m(self, f), middlewares, self.fetch)

    # ===================
    # Reporter operations
    # ===================

    def report_news(self, *news):
        self.backend.save_news(*news)

    async def report_visited(self):
        with (await self.chief._visited_urls_lock):
            self.chief._visited_urls.add(self.url)

    async def already_visited(self, url):
        with (await self.chief._visited_urls_lock):
            return url in self.chief._visited_urls

    async def get_worthy_urls(self, news):
        atags = BeautifulSoup(news.content, 'html.parser')('a')

        # expand relative / absolute / external urls
        raws = {a['href'] for a in atags if a.has_attr('href')}
        expended = {fillurl(self.chief.url, r) for r in raws}

        # return only worthy urls
        worthies = await asyncio.gather(*[
            self.worth_to_visit(news, e) for e in expended
        ])
        return {e for e, w in zip(expended, worthies) if w}

    async def worth_to_visit(self, news, url):
        root_url = self.chief.url
        filter_options = self.filter_options
        experience = self.meta.fetch_experience

        brothers = filter_options.get('brothers')
        max_depth = filter_options.get('max_depth')
        max_dist = filter_options.get('max_dist')
        blacklist = filter_options.get('blacklist')

        is_child = issuburl(root_url, url)
        is_relative = any([issuburl(b, url) for b in brothers])
        blacklist_ok = ext(url) not in blacklist
        depth_ok = depth(root_url, url) <= max_depth if max_depth else True
        dist_ok = self.distance < max_dist if max_dist else True

        # url should be either one of the relatives or child url within
        # allowed depth from the root url.
        format_ok = (is_child and depth_ok) or is_relative

        return format_ok and dist_ok and blacklist_ok and \
            not await self.already_visited(url) and \
            experience(self.schedule, news, url)

    def worth_to_report(self, news):
        return self.meta.report_experience(self.schedule, news)

    # =======================
    # Reporter callup methods
    # =======================

    def take_responsibility(self, news):
        # we don't take responsibility for root news. only non-root news are
        # valid intel.
        assert(news.src is not None)

        if news is None:
            return self

        predecessor = copy.deepcopy(self)
        predecessor.take_responsibility(news.src)

        self.url = news.url
        self.predecessor = predecessor
        self.fetched_news = news

    def summon_reporter_for(self, news):
        reporter = copy.deepcopy(self)
        reporter.take_responsibility(news)
        return reporter

    def summon_reporters_for_intel(self):
        # summon reporters responsible for news only that has same root url
        # with our chief reporter's url.
        return [self.summon_reporter_for(news) for news in self.meta.intel
                if news.root.url == self.chief.url and not news.src]

    def recruit_reporter_for(self, url):
        reporter = copy.deepcopy(self)
        reporter.url = url
        reporter.predecessor = self
        return reporter

    def recruit_reporters_for_urls(self, urls):
        return [self.recruit_reporter_for(u) for u in urls]

    def call_up_reporters(self, urls):
        # recruite new reporters for the urls and summon reporters responsible
        # for each news intel.
        recruited = self.recruit_reporters_for_urls(urls)
        summoned = self.summon_reporters_for_intel()

        return recruited + summoned
