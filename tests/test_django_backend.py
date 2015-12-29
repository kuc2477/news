from django.conf import settings
import django
import pytest

if not settings.configured:
    settings_dict = dict(
        INSTALLED_APPS=('news',),
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
            },
        }
    )

    # configure django settings
    settings.configure(**settings_dict)
    if django.VERSION >= (1, 7):
        django.setup()

def test_setup():
    pass
