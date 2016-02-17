from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils.types.url import URLType

from . import ModelBase
from ..constants import (
    NEWS_TITLE_MAX_LENGTH,
    NEWS_DESCRIPTION_MAX_LENGTH
)


Base = declarative_base()


class ScheduleMeta(ModelBase, Base):
    __tablename__ = 'schedule_meta'
    # TODO: NOT IMPLEMENTED YET

    @classmethod
    def from_domain(cls, domain_object):
        # TODO: NOT IMPLEMENTED YET
        pass

    def to_domain(self):
        # TODO: NOT IMPLEMENTED YET
        pass


class News(ModelBase, Base):
    __tablename__ = 'news'

    site = Column(URLType)
    url = Column(URLType, primary_key=True)
    src_url = Column(Integer, ForeignKey('news.url'))
    src = Column(Integer, back_populates='news_list')

    title = Column(String(NEWS_TITLE_MAX_LENGTH))
    content = Column(Text)
    description = Column(String(NEWS_DESCRIPTION_MAX_LENGTH))
    image = Column(URLType)

    def __str__(self):
        return self.url

    @classmethod
    def from_domain(cls, domain_object):
        # TODO: NOT IMPLEMENTED YET
        pass

    def to_domain(self):
        # TODO: NOT IMPLEMENTED YET
        pass
