""":mod:`news.models` --- Abstract News model interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides abstract common news model interfaces that should be implemeted
backends.

"""
from celery import states
from bs4 import BeautifulSoup
from extraction import Extractor
from ..utils import url


__all__ = ['AbstractModel', 'AbstractSchedule', 'AbstractNews']


# ===============
# Abstract models
# ===============

class AbstractModel(object):
    """Provides common model interface that should be implemented by
    backends."""

    #: (:class:`int`) Id or primary key of the model.
    id = NotImplementedError


class AbstractSchedule(AbstractModel):
    """Provides schedule meta model interface that should be implemented by
    backends."""

    #: (class:`~news.models.abstract.AbstractModel` implementation) Owner of
    #: the schedule.
    owner = NotImplementedError

    #: (:class:`str`) Url of the schedule.
    url = NotImplementedError

    #: (:class:`bool`) Schedule activation status.
    enabled = NotImplementedError

    #: (:class:`int`) Schedule's news update cycle in minutes.
    cycle = NotImplementedError

    #: (:class:`int`) Maximum urls allowed for reporters to discover.
    max_visit = NotImplementedError

    #: (:class:`int`) Maximum distance allowed for reporters to discover.
    max_dist = NotImplementedError

    #: (:class:`int`) Maximum depth allwoed for reporters to discover.
    max_depth = NotImplementedError

    #: (:class:`list`) Filetype blacklist that reporters should not visit.
    blacklist = NotImplementedError

    #: (:class:`list`) List of urls allowed for reporters to visit even if
    #: other conditions are not met (e.g. not under same domain).
    brothers = NotImplementedError

    #: (:class:`str`) UUID of the latest celery task that has been run.
    latest_task = NotImplementedError

    @property
    def filter_options(self):
        """
        Returns filter options (:attr:`max_dist`, :attr:`max_depth` ...) of
        the schedule.

        :returns: Filter options to be used by reporters when discovering news.
        :rtype: :class:`dict`

        """
        return {
            'max_visit': self.max_visit,
            'max_dist': self.max_dist,
            'max_depth': self.max_depth,
            'blacklist': self.blacklist,
            'brothers': self.brothers
        }

    def get_state(self, celery):
        try:
            return celery.AsyncResult(str(self.id)).state
        except Exception:
            return states.PENDING


class AbstractNews(AbstractModel):
    """
    Provides news model interface that should be implemented by backends.
    It also contains some default implementations for derivative properties.

    """

    @classmethod
    def create_instance(cls, schedule, url, content, src=None):
        """
        Provides common interface to create models and abstracts different
        behaviours of model constructors away from various types of orms.

        :param schedule: Schedule that fetched the news.
        :type schedule: :class:`~news.models.AbstractSchedule` implementation
        :param url: Url of the news.
        :type url: :class:`str`
        :param content: Content of the news.
        :type content: :class:`str`
        :param src: Parent news of the news.
        :type src: :class:`~news.models.AbstractNews` implementation
        :returns: Should return instance of a News fetched by a reporter.
        :rtype: :class:`~news.models.AbstractNews` implementation

        """
        raise NotImplementedError

    #: (:class:`str`) Url of the news.
    url = NotImplementedError

    #: (:class:`str`) Content of the news.
    content = NotImplementedError

    #: (:class:`~news.models.abstract.AbstractSchedule` implementation)
    #: Schedule that the news belongs to.
    schedule = NotImplementedError

    #: (:class:`~news.models.abstract.AbstractNews` implementation)
    #: Parent news from which the url of the news has been found.
    src = NotImplementedError

    #: (:class: `~datetime.datetime`)
    #: Created datetime.
    created = NotImplementedError

    #: (:class: `~datetime.datetime`)
    #: Updated datetime.
    updated = NotImplementedError

    @property
    def owner(self):
        """(:class:`~news.models.abstract.AbstractModel` implementation) Owner
        of the news."""
        return self.schedule.owner

    @property
    def root(self):
        """(:class:`~news.models.abstract.AbstractNews` implementation) Root
        news of the news."""
        return self if not self.src else self.src.root

    @property
    def is_root(self):
        """(:class:`bool`) Returns `True` if the news is root news."""
        return self.src is None

    @property
    def depth(self):
        """(:class:`int`) Depth from the root news."""
        return url.depth(self.root.url, self.url)

    @property
    def distance(self):
        """(:class:`int`) Distance from the root news."""
        return 0 if not self.src else self.src.distance + 1

    @property
    def extracted(self):
        try:
            extracted = self._cached_extracted
        except AttributeError:
            extracted = self._cached_extracted = \
                Extractor().extract(self.content)

        return extracted

    @property
    def soup(self):
        try:
            soup = self._cached_soup
        except AttributeError:
            soup = self._cached_soup = BeautifulSoup(self.content)

        return soup

    @property
    def text(self):
        try:
            return self._cached_text

        except AttributeError:
            # kill all script and style elements
            for script in self.soup(['script', 'style']):
                script.extract()    # rip it out

            # get text
            text = self.soup.get_text()

            # break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for
                      phrase in line.split("  "))
            # drop blank lines
            self._cached_text = '\n'.join(chunk for chunk in chunks if chunk)

        finally:
            return self._cached_text

    @property
    def words(self):
        tokenized = self.text.replace('\n', ' ').split(' ')
        return (w for w in tokenized if w.isalpha())

    @property
    def title(self):
        """(:class:`str`) Extracted title of the news."""
        return self.extracted.title

    @property
    def image(self):
        """(:class:`str`) Extracted url of the news image."""
        return self.extracted.image

    @property
    def description(self):
        """(:class:`str`) Extracted description of the news."""
        return self.extracted.description
