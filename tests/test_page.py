import json

from bs4 import BeautifulSoup
import asyncio
import pytest

from fixtures import *


def test_text_page_urls(text_page):
    assert(len(text_page.get_worthy_urls()) == 0)

def test_local_link_page_urls(local_link_page):
    assert(len(local_link_page.get_worthy_urls()) == 1)

def test_external_link_page_urls(external_link_page):
    assert(len(external_link_page.get_worthy_urls()) == 0)

def test_hash_link_page_urls(hash_link_page):
    assert(len(hash_link_page.get_worthy_urls()) == 1)

def test_json_serialization(page):
    json.dumps(page.to_json())

def test_is_anchor_valid(page, external_link_content):
    anchors = BeautifulSoup(external_link_content)('a')
    assert(not page.worth_visit(anchors[0]['href'], maxdepth=1, maxdist=1,
                             blacklist=[]))
