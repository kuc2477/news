""":mod:`news.reporters.mixins` --- Generic reporter mixins
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides generic reporter mixins.

"""
from .generics import TraversingReporter
from ..utils.url import (
    issamedomain,
    issuburl,
    ext,
)
from ..constants import (
    DEFAULT_EXT_BLACKLIST,
    DEFAULT_MAX_VISIT,
)


class BatchTraversingMixin(object):
    def __init__(self, intel=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._intel = intel or []
        self.__summoned_reporter_cache = {}

    def recruit_reporters(self, urls=None):
        recruited = super().recruit_reporters(urls)
        summoned = self._summon_reporters(self._intel)
        return recruited + summoned

    def _summon_reporters(self, news_list):
        if not isinstance(self, TraversingReporter):
            return []
        else:
            return [self._summon_reporter(n) for n in news_list]

    def _summon_reporter(self, news):
        cache = self.__summoned_reporter_cache
        # find summoned reporter in cache first
        try:
            return cache[news]
        # inherit meta to new reporter when not found
        except KeyError:
            parent = self.root if news.parent.is_root else \
                self.root._summon_reporter(news.parent)
            reporter = cache[news] = self._inherit_meta(
                url=news.url, parent=parent
            )
            reporter.fetched_news = news
            return reporter


class DomainTraversingMixin(object):
    async def filter_urls(self, news, *urls):
        root_url = self.root.url

        # options
        url_whitelist = self.options.get('url_whitelist', [])
        url_blacklist = self.options.get('url_blacklist', [])
        ext_blacklist = self.options.get('ext_blacklist',
                                         DEFAULT_EXT_BLACKLIST)
        max_dist = self.options.get('max_dist', None)
        max_visit = self.options.get('max_visit', DEFAULT_MAX_VISIT)

        # current state
        visited = len(await self.get_visited())
        filtered = []

        for count, url in enumerate(urls, start=1):
            # conditions
            already_visited = await self.already_visited(url)
            is_same_domain = issamedomain(root_url, url)
            is_url_white = any([issuburl(w, url) for w in url_whitelist])
            is_url_black = any([issuburl(b, url) for b in url_blacklist])
            ext_ok = ext(url) not in ext_blacklist
            distance_ok = self.distance + 1 <= max_dist if max_dist else True
            visit_count_ok = visited + count <= max_visit \
                if max_visit else True

            ok = (not already_visited) and \
                (is_same_domain or is_url_white) and \
                not is_url_black and \
                ext_ok and \
                distance_ok and \
                visit_count_ok

            if ok:
                filtered.append(url)

        return filtered
