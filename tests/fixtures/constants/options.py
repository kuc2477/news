import pytest
from news.constants import DEFAULT_BLACKLIST


@pytest.fixture(params=[3, 4, 5, 30, 40, 50, 100])
def cycle(request):
    return request.param

@pytest.fixture(params=[0, 1, 2, 3, 4, 5])
def max_dist(request):
    return request.param

@pytest.fixture(params=[0, 1, 2, 3, 4 , 5])
def max_depth(request):
    return request.param

@pytest.fixture
def blacklist():
    return DEFAULT_BLACKLIST

@pytest.fixture
def brothers():
    return []
