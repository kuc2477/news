import copy
from ..models import AbstractSchedule
from ..reporters import Reporter


class Mapping(object):
    """Mapping from news type / schedules to reporter classes.

    Implements `__setitem__` and `__getitem__` magic methods to support both
    mapping from :class:`str` to :class:`~news.reporters.Reporter` subclasses
    and from :class:`~news.models.AbstractSchedule` subclasses to
    `~news.reporters.Reporter`.

    :param mapping: A mapping to inherit from.
    :type mapping: :class:`~news.scheduler.Mapping`

    """
    def __init__(self, mapping=None):
        if isinstance(mapping, dict):
            self.__map = mapping
        elif isinstance(mapping, Mapping):
            self.__map = mapping.as_dict()
        else:
            raise TypeError('Only dictionary or `Mapping` instance is allowed')

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
            return self.__map[key]
        elif isinstance(key, AbstractSchedule):
            return self.__map[key.news_type]
        else:
            raise KeyError('Only Schedule subclass or string are allowed ' +
                           'as mapping key')

    def __contains__(self, key):
        return key in self.__map

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

    def merge(self, mapping):
        """Merge another mapping.

        :param mapping: A mapping to merge.
        :type mapping: :class:`Mapping`
        :returns: Merged mapping itself
        :rtype: :class:`Mapping`

        """
        self.__map.update(mapping)
        return self

    @classmethod
    def from_dict(cls, mapping):
        """Create a mapping from a dictionary.

        :param mapping: Mapping dictionary to use.
        :type mapping: :class:`dict`

        """
        assert(isinstance(mapping, dict)), 'Only `dict` type is allowed'
        return cls(mapping=mapping)

    def as_dict(self):
        """Returns internal mapping dictionary as a copied dictionary.

        :returns: Mapping dictionary.
        :rtype: :class:`dict`

        """
        return copy.deepcopy(self.__map)
