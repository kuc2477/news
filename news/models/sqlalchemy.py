from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types.url import URLType

from ..constants import (
    NEWS_TITLE_MAX_LENGTH,
    NEWS_DESCRIPTION_MAX_LENGTH
)


Base = declarative_base()


class Site(Base):
    __tablename__ = 'site'

    url = Column(URLType, primary_key=True)


class News(Base):
    __tablename__ = 'news'

    url = Column(URLType, primary_key=True)
    content = Column(Text)
    title = Column(String(NEWS_TITLE_MAX_LENGTH))
    description = Column(String(NEWS_DESCRIPTION_MAX_LENGTH))

    site_url = Column(Integer, ForeignKey('site.url'))
    site = relationship('Site', back_populates='news_list')

    src_url = Column(Integer, ForeignKey('news.url'))
    src = Column(Integer, back_populates='news_list')
