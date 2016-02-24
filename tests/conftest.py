from django.conf import settings
from fixtures import *


DJANGO_SETTINGS_DICT = dict(
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'news',
    ),
    DATABASES={
        "default": {
            "NAME": "__NEWS_TEST_DB__",
            "ENGINE": "django.db.backends.sqlite3",
        },
    }
)


def pytest_configure():
    # configure django settings
    settings.configure(**DJANGO_SETTINGS_DICT)
