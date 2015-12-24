import json

import asyncio
import pytest

from .fixtures import *



def test_text_page_links(text_page) :
    assert(len(text_page.links) == 0)

def test_local_link_page_links(local_link_page):
    assert(len(local_link_page.links) == 1)

def test_external_link_page_links(external_link_page):
    assert(len(external_link_page.links) == 0)

def test_hash_link_page_links(hash_link_page):
    assert(len(hash_link_page.links) == 1)

def test_text_page_urls(text_page):
    assert(len(text_page.urls) == 0)

def test_local_link_page_urls(local_link_page):
    assert(len(local_link_page.urls) == 1)

def test_external_link_page_urls(external_link_page):
    assert(len(external_link_page.urls) == 0)

def test_hash_link_page_links(hash_link_page):
    assert(len(hash_link_page.urls) == 1)

def test_json_serialization(page):
    json.dumps(page.to_json())
