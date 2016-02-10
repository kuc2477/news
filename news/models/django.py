from django.db import models

from ..constants import (
    NEWS_TITLE_MAX_LENGTH,
    NEWS_DESCRIPTION_MAX_LENGTH
)


# TODO: NOT IMPLEMENTED YET
class ScheduleMeta(models.Model):
    pass


class News(models.Model):
    site = models.URLField()
    url = models.URLField(primary_key=True)
    src = models.ForeignKey('self', related_name='children', db_index=True,
                            blank=True, null=True)

    title = models.CharField(max_length=NEWS_TITLE_MAX_LENGTH)
    content = models.TextField()
    description = models.CharField(max_length=NEWS_DESCRIPTION_MAX_LENGTH)
    image = models.URLField()

    def __str__(self):
        return self.url
