from .generics import TraversingReporter
from ..constants import (
    DEFAULT_BLACKLIST,
    DEFAULT_MAX_VISIT,
)


class BatchTraversingMixin(object):
    def __init__(self, intel=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._intel = intel or []
        self.__summoned_reporter_cache = {}

    def recruit_reporters(self, targets):
        recruited = super().recruit_reporters(targets)
        summoned = self._summon_reporters(self._intel)
        return recruited + summoned

    def _summon_reporters(self, news_list):
        if not isinstance(self, TraversingReporter):
            return []
        else:
            return [self._summon_reporters(n) for n in news_list]

    def _summon_reporter(self, news):
        cache = self.__summoned_reporter_cache
        # find summoned reporter in cache first
        try:
            return cache[news]
        # inherit meta to new reporter when not found
        except KeyError:
            parent = self.root if news.parent.is_root else \
                self.root.summon_reporter(news.parent)

            reporter = cache[news] = self._inherit_meta(
                target=news.target, parent=parent
            )
            return reporter


class DomainTraversingMixin(object):
    def worth_to_visit(self, news, target):
        brothers = self.options.get('brothers', [])
        max_dist = self.options.get('max_dist', None)
        max_depth = self.options.get('max_depth', None)
        max_visit = self.options.get('max_visit', DEFAULT_MAX_VISIT)
        blacklist = self.options.get('blacklist', DEFAULT_BLACKLIST)
        return True
