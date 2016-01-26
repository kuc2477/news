import json

from bs4 import BeautifulSoup

from fixtures import *


def test_text_news_urls(text_news):
    assert(len(text_news.get_worthy_urls()) == 0)


def test_local_link_news_urls(local_link_news):
    assert(len(local_link_news.get_worthy_urls()) == 1)


def test_external_link_news_urls(external_link_news):
    assert(len(external_link_news.get_worthy_urls()) == 0)


def test_hash_link_news_urls(hash_link_news):
    assert(len(hash_link_news.get_worthy_urls()) == 1)


def test_json_serialization(news):
    json.dumps(news.to_json())


def test_is_anchor_valid(news, external_link_content):
    anchors = BeautifulSoup(external_link_content)('a')
    assert(not news.worth_visit(
        anchors[0]['href'], maxdepth=1, maxdist=1, blacklist=[]
    ))
