import pytest
from celery import Celery


@pytest.fixture(scope='session')
def celery():
    return Celery()
