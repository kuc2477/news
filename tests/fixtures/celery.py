import pytest
import celery


@pytest.fixture(scope='session')
def celery():
    return celery.Celery()
