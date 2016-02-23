from django.conf import settings


DJANGO_SETTINGS_DICT = dict(
    INSTALLED_APPS=('news',),
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
