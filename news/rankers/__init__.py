import abc


class BaseRanker(metaclass=abc.ABCMeta):
    """Abstract base class for ranking pages retrieved from the site.

    Provides common iterface for site to filter out meaningless pages from
    the fetched pages.

    """

    @abc.abstractmethod
    def rank(self, pages):
        """Rank scores on the pages.

        :param pages: Pages to rank scores.
        :type pages: :class:`list`
        :return: Scores of the pages.
        :rtype: :class:`list`

        """
        return NotImplemented

    @abc.abstractmethod
    def get_meaningful_pages(self, pages, n=10):
        """Sort out meaningful pages from fetched pages of the site.

        :param pages: Pages to be sorted out.
        :type pages: :class:`list`
        :return: Filtered pages.
        :rtype: :class:`list`

        """
        ranked =  list(zip(pages, self.rank(pages))).sort(lambda x: x[1])
        return x[1] for x in ranked][:n]
