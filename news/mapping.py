""":mod:`news.mapping` --- News reporter mapping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provide a mapping class that maps from schedule to reporter classes.

"""
import copy
from ..models import AbstractSchedule
from ..reporters import Reporter
from ..reporters.url import URLReporter
from ..reporters.feed import (
    AtomReporter,
    RSSReporter
)


def merge_kwargs_factories(kwargs_factories):
    """Merge news type keyed kwargs factory functions into a single factory.

    :param kwargs_factories: A dictionary of news type keyed kwargs factory
        functions.
    :type kwargs_factories: :class:`dict`
    :returns: A merged kwargs factory.
    :rtype: A factory function that takes an schedule and returns kwargs dict.

    """
    def merged_factory(schedule):
        try:
            return kwargs_factories[schedule.news_type](schedule)
        except KeyError:
            return {}

    return merged_factory


class Mapping(object):
    """Mapping from news type / schedule to reporter classes.

    Implements `__setitem__` and `__getitem__` magic methods to support both
    mapping from :class:`str` to :class:`~news.reporters.Reporter` subclasses
    and from :class:`~news.models.AbstractSchedule` subclasses to
    `~news.reporters.Reporter`.

    :param mapping: A mapping to inherit from.
    :type mapping: :class:`~news.scheduler.Mapping` or `dict`
    :param kwargs_factory: A **kwargs factory function that takes an schedule
        and returns appropriate reporter kwargs. Factory functions will be
        merged if a dictionary which maps from news types to kwargs factory is
        given. Defaults to a function that simply returns empty dictionary.
    :type kwargs_factory: A function that takes an
        :class:`~news.models.AbstractSchedule` implementation's instance and
        returns a reporter kwargs dictionary. A dictioanry mapped from
        news types to kwargs factory function is also allowed.

    *Example*::

        from news.mapping import DefaultMapping
        from news.reporters.url import URLReporter

        # both two formats are legal. later one will be merged into a single
        # factory based on it's news types.
        kwargs_factory = (lambda schedule: {'some_kwarg': 1})
        kwargs_factory = {
            'url': (lambda schedule: {'some_kwarg': 1})
        }

        # create an mapping
        mapping = DefaultMapping(kwargs_factory=kwargs_factory)

        ...

        # get reporter by news type string (returns empty kwargs)
        reporter_class, kwargs = mapping['url']
        assert(reporter_class == URLReporter)
        assert(not kwargs)

        # get reporter  by schedule instance (returns kwargs from factory)
        reporter_class, kwargs = mapping[schedule]
        assert(reporter_class == URLReporter)
        assert(kwargs['some_kwarg'] == 1)

        # our main purpose to use mapping
        reporter = reporter_class(meta=meta, backend=backend, **kwargs)

    """
    def __init__(self, mapping=None, kwargs_factory=None):
        if mapping is None:
            self.__map = {}
        elif isinstance(mapping, dict):
            self.__map = mapping
        elif isinstance(mapping, Mapping):
            self.__map = mapping.as_dict()
            self.__kwargs_factory = mapping.kwargs_factory
        else:
            raise TypeError('Only dictionary or `Mapping` instance is allowed')

        if kwargs_factory is None:
            self.__kwargs_factory = (lambda schedule: {})
        elif callable(kwargs_factory):
            self.__kwargs_factory = kwargs_factory
        elif isinstance(kwargs_factory, dict):
            self.__kwargs_factory = merge_kwargs_factories(kwargs_factory)
        else:
            raise TypeError('Only factory or dictionary of factories are ' +
                            'allowed')

    def __setitem__(self, key, value):
        # only reporters can be mapped to
        if not isinstance(value, Reporter):
            raise ValueError('Only reporter subclasses can be mapped to')

        if isinstance(key, str):
            self.__map[key] = value
        elif isinstance(key, AbstractSchedule):
            self.__map[key.news_type] = value
        # only string or schedule can be mapped from
        else:
            raise KeyError('Mapping key is only allowed for Schedule ' +
                           'subclass or string')

    def __getitem__(self, key):
        # only string or schedule can be mapped from.
        if isinstance(key, str):
            return self.__map[key], {}
        elif isinstance(key, AbstractSchedule):
            return self.__map[key.news_type], self._make_kwargs(key)
        else:
            raise KeyError('Only Schedule subclass or string are allowed ' +
                           'as mapping key')

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def _make_kwargs(self, schedule):
        return self.__kwargs_factory(schedule)

    def map(self, key, value):
        """Add mapping from a news type or a schedule to a reporter class.

        :param key: Schedule or an string to be mapped from.
        :type key: A `~news.models.AbstractSchedule` implementation or
            :class:`str`
        :param value: Reporter to be mapped to.
        :type value: `~news.reporters.Reporter`
        :returns: Modified mapping itself
        :rtype: :class:`Mapping`

        """
        self[key] = value
        return self

    def unmap(self, key):
        """Remove mapping from a news type or a schedule to a reporter class.

        :param key: Schedule or an string mapped from.
        :type key: A `~news.models.AbstractSchedule` implementation or
            :class:`str`
        :returns: Modified mapping itself
        :rtype: :class:`Mapping`

        """
        del self[key]
        return self

    def merge(self, mapping, kwargs_factory=None):
        """Merge another mapping.

        :param mapping: A mapping to merge.
        :type mapping: :class:`dict` or :class:`Mapping`
        :param kwargs_factory: A kwargs factory function to set.
        :type kwargs_factory: A function that takes an schedule and returns
            appropriate kwrags dict.
        :returns: The merged mapping itself
        :rtype: :class:`Mapping`

        """
        if isinstance(mapping, dict):
            self.__map.update(mapping)
        elif isinstance(mapping, Mapping):
            self.__map.update(mapping.as_dict())
            self.__kwargs_factory = mapping.kwargs_factory
        else:
            raise TypeError('Only dictionary or `Mapping` instance is allowed')

        if kwargs_factory:
            self.__kwargs_factory = kwargs_factory

        return self

    @classmethod
    def from_dict(cls, mapping, kwargs_factory=None):
        """Create a mapping from a dictionary.

        :param mapping: Mapping dictionary to use.
        :type mapping: :class:`dict`
        :param kwargs_factory: A kwargs factory function.
        :type kwargs_factory: A function that takes an schedule and returns
            appropirate reporter kwargs dict.

        """
        assert(isinstance(mapping, dict)), 'Only `dict` type is allowed'
        return cls(mapping=mapping, kwargs_factory=kwargs_factory)

    def as_dict(self):
        """Returns internal mapping dictionary as a copied dictionary.

        :returns: Mapping dictionary.
        :rtype: :class:`dict`

        """
        return copy.deepcopy(self.__map)

    @property
    def kwargs_factory(self):
        """Returns kwargs factory function.

        :returns: A kwargs factory function.
        :rtype: A function that takes an schedule and returns reporter kwargs
            dict.

        """
        return self.__kwargs_factory


class DefaultMapping(Mapping):
    """Default mapping implementation.

    Maps 'url', 'atom', 'rss' news types to `news.reporters.url.URLReporter`,
    `news.reporters.feed.AtomReporter` and `news.reporters.feed.RSSReporter`.

    :param mapping: A mapping to merge into default mapping.
    :type mapping: :class:`~news.scheduler.Mapping` or `dict`

    """
    __default = {
        'url': URLReporter,
        'atom': AtomReporter,
        'rss': RSSReporter,
    }

    def __init__(self, mapping=None, kwarg_factory=None):
        mapping = Mapping(mapping=self.__default).merge(mapping)
        super().__init__(mapping=mapping, kwarg_factory=kwarg_factory)
