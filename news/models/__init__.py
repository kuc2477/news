import os

if 'DJANGO_SETTINGS_MODULE' in os.environ:
    from .django import Schedule, News
