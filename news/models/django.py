from django.db import models


URL_MAX_LENGTH = 300


class Site(models.Model):
    url = models.CharField(max_length=URL_MAX_LENGTH, primary_key=True)

    def __str__(self):
        return self.url


class Page(models.Model):
    url = models.CharField(max_length=URL_MAX_LENGTH, primary_key=True)
    site = models.ForeignKey(Site, related_name='pages', db_index=True)
    src = models.ForeignKey('self', related_name='children', db_index=True,
                            blank=True, null=True)
    content = models.TextField()

    def __str__(self):
        return self.url
