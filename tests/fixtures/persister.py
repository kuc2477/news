import pytest
from redis import Redis
from news.persister import Persister


@pytest.fixture(scope='session')
def persister():
    redis = Redis()
    return Persister(redis=redis)
