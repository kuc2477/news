from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils.types.url import URLType

from .abstract import ModelBase
from ..constants import (
    NEWS_TITLE_MAX_LENGTH,
    NEWS_DESCRIPTION_MAX_LENGTH
)


Base = declarative_base()


class Schedule(ModelBase, Base):
    __tablename__ = 'schedule'
    # TODO: NOT IMPLEMENTED YET


class News(ModelBase, Base):
    __tablename__ = 'news'

    url = Column(URLType)
    content = Column(Text)
    src_url = Column(Integer, ForeignKey('news.url'))
    src = Column(Integer, back_populates='news_list')


