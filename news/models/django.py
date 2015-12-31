from django.db import models


URL_MAX_LENGTH = 300


class Page(models.Model):
    url = models.CharField(max_length=URL_MAX_LENGTH, primary_key=True)
    site = models.CharField(max_length=URL_MAX_LENGTH)
    src = models.ForeignKey('self', related_name='children', db_index=True,
                            blank=True, null=True)

    content = models.TextField()
