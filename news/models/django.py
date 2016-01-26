from django.db import models

from ..constants import (
    NEWS_TITLE_MAX_LENGTH,
    NEWS_DESCRIPTION_MAX_LENGTH
)


class Site(models.Model):
    url = models.URLField(primary_key=True)

    def __str__(self):
        return self.url


class News(models.Model):
    url = models.URLField(primary_key=True)
    site = models.ForeignKey(Site, related_name='pages', db_index=True)
    src = models.ForeignKey('self', related_name='children', db_index=True,
                            blank=True, null=True)
    content = models.TextField()

    title = models.CharField(max_length=NEWS_TITLE_MAX_LENGTH)
    description = models.CharField(max_length=NEWS_DESCRIPTION_MAX_LENGTH)
    image = models.URLField()

    def __str__(self):
        return self.url
