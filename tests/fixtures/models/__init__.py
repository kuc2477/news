import pytest
from news.models import Readable
from .django import *
from .sqlalchemy import *


@pytest.fixture
def readable_root(author_root, title_root, content_root, summary_root):
    return Readable(author=author_root, title=title_root,
                    content=content_root, summary=summary_root)


@pytest.fixture
def readable_child(author_child, title_child, content_child, summary_child):
    return Readable(author=author_child, title=title_child,
                    summary=summary_child, content=content_child)
