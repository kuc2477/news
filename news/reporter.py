""":mod:`news.reporter` --- News reporters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides :class:`~news.reporter.Reporter` class and it's derivatives.

"""
from functools import reduce
import itertools
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from .utils.url import (
    ext, issuburl, fillurl,
    normalize, depth
)
from .utils.python import importattr


__all__ = ['ReporterMeta', 'Reporter']


class ReporterMeta(object):
    """
    Meta information / options to be used by reporters.

    :param schedule: Schedule which created the chief reporter of the
        reporter or reporter itself. Schedule provides necessary information
        such as the owner of the schedule or filter options to use in news
        fetching process.
    :type schedule: Implementation of :class:`~news.models.AbstractSchedule`.
    :param intel: A list of news that was fetched in the past.
        Reporters responsible for each news of intel will be
        summoned by the reporter and dispatched along with the reporters
        recruited for the urls of the fetched news. This can work as a
        performance boost since reporters summoned for each news of
        intel can be dispatched without wating for their
        predecessors to dispatch them.
    :type intel: :class:`list`
    :param report_experience: A function that takes schedule of the news and a
        news as arguments and returns `True` if the news is valuable,
        considered valuable, or return `False` otherwise.
    :type report_experience: :func:
    :param fetch_experience: A function that takes schedule of the news and a
        news that contains urls and a url as arguments and returns `True` if
        the url is valuable, or return `False` otherwise.
    :type fetch_experience: :func:

    """

    def __init__(self, schedule, intel=None,
                 report_experience=None,
                 fetch_experience=None):
        # Schedule meta that contains information about owner and
        # filter options.
        self.schedule = schedule

        # Intel (list of news) to be used for batch-fetching, which will
        # impreove performance of the chief reporter's initial fetch.
        self.intel = intel or []

        # Experience of the reporter, which will filter out meaningless
        # urls or news, thus improve performance of the reporter.
        self.report_experience = report_experience
        self.fetch_experience = fetch_experience

    def exhaust_intel(self):
        intel = self.intel
        self.intel = []
        return intel

    @property
    def owner(self):
        """
        (:class:`~news.models.AbstractOwnerMixin` implementation of the
        :attr:`schedule`'s backend type) The owner of the schedule meta that
        is used to instantiate this reporter meta.

        """
        return self.schedule.owner

    @property
    def filter_options(self):
        """(:class:`dict`) Filter options to be used by reporters."""
        return self.schedule.filter_options


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

        # keep applied middlewares to inherit to successors
        self._applied_dispatch_middlewares = []
        self._applied_fetch_middlewares = []

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

    @property
    def chief(self):
        return self if self.is_chief else self.predecessor.chief

    @property
    def is_chief(self):
        return self.predecessor is None

    @property
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
        # fetch news from the url and determine whether it is worthy or not
        news = await self.fetch()
        news = news if news and self.worth_to_report(news) else None

        # report fetched news immediately if we are not going to report bulk
        if news and not bulk_report:
            self.report_news(news)

        urls = await self.get_worthy_urls(news) if news else []
        news_linked = await self.dispatch_reporters(urls, bulk_report)
        news_total = news_linked + [news] if news else news_linked

        # Bulk report news if the flag is set to `True`. We don't have to
        # take care of case of `False` since news should be reported on
        # `dispatch()` calls of each successor reporters already if
        # `bulk_report` flag was given `True`.
        if bulk_report and self.is_chief:
            self.report_news(*set(news_total))

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
        reporters = self.call_up_reporters(urls, self.meta.exhaust_intel())

        # return empty list if no reporters has been called up
        if not reporters:
            return []

        dispatches = [r.dispatch(bulk_report=bulk_report) for r in reporters]

        news_sets = await asyncio.gather(*dispatches, return_exceptions=True)
        news_list = list(itertools.chain(*[
            ns for ns in news_sets if ns and not isinstance(ns, Exception)
        ]))

        return news_list

    async def fetch(self):
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
            # return nothing if status code is not OK
            if response.status != 200:
                return None

            # report to the chief reporter that we visited the url.
            await self.report_visited()

            # make news from response and set fetched
            self.fetched_news = self.make_news(await response.text())
            return self.fetched_news

    # ====
    # News
    # ====

    def make_news(self, content):
        src = self.predecessor.fetched_news if not self.is_chief else None

        # we might already have previously fetched or stored news.
        fetched = self.fetched_news
        stored = self.backend.get_news_by(owner=self.owner, url=self.url)

        # create new news if reporter is making fresh news.
        if not fetched and not stored:
            return self.backend.News.create_instance(
                self.schedule, self.url, content, src=src
            )
        # update content and source if the reporter is updating the news.
        else:
            news = fetched or stored
            news.content = content
            news.src = src
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
        self._applied_dispatch_middlewares += middlewares
        self.dispatch = reduce(
            lambda d, m: m(self, d),
            [importattr(path) for path in middlewares],
            self.dispatch
        )
        return self

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
        self._applied_fetch_middlewares += middlewares
        self.fetch = reduce(
            lambda f, m: m(self, f),
            [importattr(path) for path in middlewares],
            self.fetch
        )
        return self

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

    async def get_visited_urls(self):
        with (await self.chief._visited_urls_lock):
            return self.chief._visited_urls

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
        experience = importattr(self.meta.fetch_experience) \
            if self.meta.fetch_experience else lambda s, n, u: True

        brothers = filter_options.get('brothers')
        max_visit = filter_options.get('max_visit')
        max_depth = filter_options.get('max_depth')
        max_dist = filter_options.get('max_dist')
        blacklist = filter_options.get('blacklist')

        is_child = issuburl(root_url, url)
        is_relative = any([issuburl(b, url) for b in brothers])
        blacklist_ok = ext(url) not in blacklist
        visit_count_ok = len(await self.get_visited_urls()) <= max_visit
        already_visited = await self.already_visited(url)
        depth_ok = depth(root_url, url) <= max_depth if max_depth else True
        dist_ok = self.distance < max_dist if max_dist else True

        # url should be either one of the relatives or child url within
        # allowed depth from the root url.
        format_ok = (is_child and depth_ok) or is_relative

        result = format_ok and dist_ok and visit_count_ok and blacklist_ok and\
            not already_visited and \
            (experience(self.schedule, news, url) if experience else True)

        return result

    def worth_to_report(self, news):
        experience = importattr(self.meta.report_experience) \
            if self.meta.report_experience else lambda s, n: True
        return experience(self.schedule, news)

    # =======================
    # Reporter callup methods
    # =======================

    def inherit_meta(self, url, predecessor=None):
        reporter = Reporter(url, self.meta, self.backend)
        reporter.enhance_fetch(*self._applied_fetch_middlewares)
        reporter.predecessor = predecessor or self
        return reporter

    def summon_reporter_for(self, news):
        try:
            cache = self._summoned_reporter_cache
        except AttributeError:
            cache = self._summoned_reporter_cache = {}

        try:
            return cache[news]
        except KeyError:
            reporter = cache[news] = self.inherit_meta(
                news.url, predecessor=(
                    self.chief if news.src.is_root else
                    self.chief.summon_reporter_for(news.src)
                )
            )
            reporter.fetched_news = news
            return reporter

    def summon_reporters_for_intel(self, intel):
        return [self.summon_reporter_for(news) for news in intel
                if news.schedule == self.schedule and news.src]

    def recruit_reporter_for(self, url):
        return self.inherit_meta(url)

    def recruit_reporters_for_urls(self, urls):
        return [self.recruit_reporter_for(u) for u in urls]

    def call_up_reporters(self, urls, intel):
        # recruite new reporters for the urls and summon reporters responsible
        # for each news intel.
        recruited = self.recruit_reporters_for_urls(urls)
        summoned = self.summon_reporters_for_intel(intel)

        return recruited + summoned
