import json

from bs4 import BeautifulSoup
import asyncio
import pytest

from fixtures import *
from news.page import is_anchor_valid_for_site


def test_text_page_urls(text_page):
    assert(len(text_page.urls) == 0)

def test_local_link_page_urls(local_link_page):
    assert(len(local_link_page.urls) == 1)

def test_external_link_page_urls(external_link_page):
    assert(len(external_link_page.urls) == 0)

def test_hash_link_page_urls(hash_link_page):
    assert(len(hash_link_page.urls) == 1)

def test_json_serialization(page):
    json.dumps(page.to_json())

def test_is_anchor_valid_for_site(site, external_link_content):
    anchors = BeautifulSoup(external_link_content)('a')
    assert(not is_anchor_valid_for_site(site, anchors[0]))
