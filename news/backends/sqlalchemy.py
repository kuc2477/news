""":mod:`news.backends.sqlalchemy` --- News backend SQLAlchemy implementations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides an implementation of news backend for sqlalchemy projects.

"""
from sqlalchemy.orm import sessionmaker
from . import AbstractBackend


class HeterogenuousEngineError(Exception):
    """
    Engine error that will be raised when either given sqlalchemy models
    doesn't share common engine

    """


class SQLAlchemyBackend(AbstractBackend):
    def __init__(self, bind=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Owner = self.owner_class
        self.Schedule = self.schedule_class
        self.News = self.news_class

        # use given session if available. otherwise try to retrieve session
        # from the engine bound to models if exists.
        self.session = bind or self.retrieve_session(
            self.Owner, self.Schedule, self.News)

    def get_news(self, owner, url):
        return self.session.query(self.News)\
            .join(self.Schedule)\
            .filter(
                self.News.url == url,
                self.Schedule.owner_id == owner.id
            ).first()

    def get_news_list(self, owner=None, root_url=None):
        query = self.session.query(self.News).join(self.Schedule)

        if owner:
            query = query.filter(self.Schedule.owner == owner)
        if root_url:
            query = query.filter(self.Schedule.url == root_url)

        return query.all()

    def save_news(self, *news):
        [self.cascade_save_news(n) for n in news]

    def cascade_save_news(self, news):
        if not news.is_root:
            self.cascade_save_news(news.src)

        previous = self.get_news(news.owner, news.url)

        if previous:
            previous.content = news.content
            previous.src = news.src
            self.session.commit()
        else:
            self.session.add(news)
            self.session.commit()

    def delete_news(self, *news):
        self.session.delete(*news)
        self.session.commit()

    def get_schedule_by_id(self, id):
        return self.session.query(self.Schedule).get(id)

    def get_schedule(self, owner, url):
        return self.session.query(self.Schedule).filter(
            self.Schedule.owner == owner,
            self.Schedule.url == url
        ).first()

    def get_schedules(self, owner=None, url=None):
        query = self.session.query(self.Schedule)

        if owner:
            query = query.filter(self.Schedule.owner == owner)
        if url:
            query = query.filter(self.Schedule.url == url)

        return query.all()

    def bind_session(self, session):
        self.session = session

    @staticmethod
    def retrieve_session(model, *models):
        if not all([m.metadata.bind for m in models + (model,)]):
            return None

        if not all([model.metadata.bind == m.metadata.bind for m in models]):
            raise HeterogenuousEngineError

        return sessionmaker(bind=model.metadata.bind)()
