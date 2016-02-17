from django.db import models

from . import ModelBase
from ..constants import (
    NEWS_TITLE_MAX_LENGTH,
    NEWS_DESCRIPTION_MAX_LENGTH
)


class ScheduleMeta(ModelBase, models.Model):
    # TODO: NOT IMPLEMENTED YET
    pass


class News(ModelBase, models.Model):
    site = models.URLField()
    url = models.URLField(primary_key=True)
    src = models.ForeignKey('self', related_name='children', db_index=True,
                            blank=True, null=True)

    title = models.CharField(max_length=NEWS_TITLE_MAX_LENGTH)
    content = models.TextField()
    description = models.CharField(max_length=NEWS_DESCRIPTION_MAX_LENGTH)
    image = models.URLField()

    def __str__(self):
        pass

    @classmethod
    def from_domain(cls, domain_object):
        # TODO: NOT IMPLEMENTED YET
        pass

        # TODO: NOT IMPLEMENTED YET
    def to_domain(self):
        pass
