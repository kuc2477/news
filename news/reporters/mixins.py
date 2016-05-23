""":mod:`news.reporters.mixins` --- Generic News Reporter Mixins
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides generic reporter mixins.

"""
from .generics import TraversingReporter
from ..utils.url import (
    issamedomain,
    issuburl,
    ext,
)
from ..constants import (
    DEFAULT_BLACKLIST,
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
            return reporter


class DomainTraversingMixin(object):
    async def worth_to_visit(self, news, url):
        root_url = self.root.url

        # options
        brothers = self.options.get('brothers', [])
        blacklist = self.options.get('blacklist', DEFAULT_BLACKLIST)
        max_dist = self.options.get('max_dist', None)
        max_visit = self.options.get('max_visit', DEFAULT_MAX_VISIT)

        # conditions
        is_same_domain = issamedomain(root_url, url)
        is_brother = any([issuburl(b, url) for b in brothers])
        blacklist_ok = ext(url) not in blacklist
        distance_ok = self.distance <= max_dist if max_dist else True
        visit_ok = len(await self.get_visited()) <= max_visit if \
            max_visit else True

        return (is_same_domain or is_brother) and \
            blacklist_ok and \
            distance_ok and \
            visit_ok
