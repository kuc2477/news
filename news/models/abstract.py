""":mod:`news.models.abstract` --- Abstract News model interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides abstract common news model interfaces that should be implemeted
backends.

"""
from cached_property import cached_property
from extraction import Extractor
from ..utils import url


__all__ = ['AbstractModel', 'AbstractSchedule', 'AbstractNews']


# ===============
# Abstract models
# ===============

class AbstractModel(object):
    """
    Provides common model interface that should be implemented by backends.

    """

    def id(self):
        """
        Should return the id of the model.

        :returns: The id of the model.
        :rtype: :class:`int`

        """
        raise NotImplementedError


class AbstractSchedule(AbstractModel):
    """
    Provides schedule meta model interface that should be implemented by
    backends.

    """

    def owner(self):
        """
        Should return a owner of the schedule.

        :returns: An owner that ownns the news schedule meta
        :rtype: Any implementation of :class:`~news.models.AbstractOwnerMixin`

        """
        raise NotImplementedError

    def url(self):
        """
        Should return target url of the schedule.

        :returns: Target url of the schedule.
        :rtype: :class:`str`

        """
        raise NotImplementedError

    def cycle(self):
        """
        Should return cycle of the schedule.

        :returns: Cycle of the schdule in minutes.
        :rtype: :class:`int`

        """
        raise NotImplementedError

    def max_dist(self):
        """
        Should return allowed maximum distance of reporter to fetch further.

        :returns: Maximum distance of reporter.
        :rtype: :class:`int`

        """
        raise NotImplementedError

    def max_depth(self):
        """
        Should return allowed maximum depth of repoter to fetch further.

        :returns: Maximum depth of reporter.
        :rtype: :class:`int`

        """
        raise NotImplementedError

    def blacklist(self):
        """
        Should return filetype blacklist that should be skipped from fetching.

        :returns: Filetype blacklist (e.g. ['png', 'gif', ...])
        :rtype: :class:`str`

        """
        raise NotImplementedError

    def brothers(self):
        """
        Should return allowed brother urls that can be fetched from site with
        different domain.

        :returns: List of urls that are allowed to be fetched from the
            schedule domain.
        :rtype: :class:`list`

        """
        raise NotImplementedError

    def get_filter_options(self):
        """
        Return filter options of the schedule.

        :returns: Filter options to be used in reporting / fetching news.
        :rtype: :class:`dict`

        """
        return {
            'max_dist': self.max_dist,
            'max_depth': self.max_depth,
            'blacklist': self.blacklist,
            'brothers': self.brothers
        }



class AbstractNews(AbstractModel):
    """
    Provides news model interface that should be implemented by backends.
    It also contains some default implementations for derivative properties.

    """

    @classmethod
    def create_instance(cls, schedule, url, content, src=None):
        """
        Provides common interface to create models and abstracts different
        behaviours of model constructors away from orms.

        :param schedule: Schedule that fetched the news.
        :type schedule: Implementation of
            :class:`~news.models.AbstractSchedule`
        :param url: Url of the news.
        :type url: :class:`str`
        :param content: Content of the news.
        :type content: :class:`str`
        :param src: Parent news of the news.
        :type src: Implementation of :class:`~news.models.AbstractNews`.
        :returns: News fetched from web by a reporter.
        :rtype: Implementation of :class:`~news.models.AbstractNews`

        """
        raise NotImplementedError

    def url(self):
        """
        Should return the url of the news.

        :returns: The url of the news.
        :rtype: :class:`str`

        """
        raise NotImplementedError

    def content(self):
        """
        Should return the content of the news.

        :returns: The content of the news.
        :rtype: :class:`str`

        """
        raise NotImplementedError

    def schedule(self):
        """
        Should return schedule of the news

        :returns: The schedule of the news.
        :rtype: Any implementation of :class:`~news.models.AbstractSchedule`

        """
        raise NotImplementedError

    def src(self):
        """
        Should return parent news of the news.

        :returns: The parent news of the news.
        :rtype: Any implementation of :class:`~news.models.AbstractNews`

        """
        raise NotImplementedError

    @property
    def owner(self):
        return self.schedule.owner

    @property
    def root(self):
        return self if not self.src else self.src.root

    @property
    def is_root(self):
        return self.src is None

    @property
    def depth(self):
        return url.depth(self.root.url, self.url)

    @property
    def distance(self):
        return 0 if not self.src else self.src.distance + 1

    @cached_property
    def extracted(self):
        return Extractor().extract(self.content)

    @property
    def title(self):
        return self.extracted.title

    @property
    def image(self):
        return self.extracted.image

    @property
    def description(self):
        return self.extracted.description
