""":mod:`news.backends.sqlalchemy` --- News backend SQLAlchemy implementations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides an implementation of news backend for sqlalchemy projects.

"""
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from .abstract import AbstractBackend


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
                self.Schedule.owner == owner
            ).first()

    def get_news_list(self, owner=None, root_url=None):
        query = self.session.query(self.News).join(self.Schedule)

        if owner:
            query = query.filter(self.Schedule.owner == owner)
        if root_url:
            query = query.filter(self.Schedule.url == root_url)

        return query.all()

    def save_news(self, *news):
        for n in news:
            if not self.news_exists(n.owner, n.url):
                self.cascade_save_news(n)
            else:
                previous = self.get_news(n.owner, n.url)
                previous.content = n.content
                previous.src = n.src
                self.session.commit()

    def cascade_save_news(self, news):
        if news.src and news.src.id is None:
            self.cascade_save_news(news.src)
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

    def set_schedule_save_listener(self, listener):
        event.listens_for(self.schedule_class, 'after_insert')(
            lambda mapper, connection, target: listener(target, created=True)
        )
        event.listens_for(self.schedule_class, 'after_update')(
            lambda mapper, connection, target: listener(target, created=False)
        )

    def set_schedule_delete_listener(self, listener):
        event.listens_for(self.schedule_class, 'after_delete')(
            lambda mapper, connection, target: listener(target)
        )

    # =====================
    # Session configuration
    # =====================

    def bind_session(self, session):
        self.session = session

    @staticmethod
    def retrieve_session(model, *models):
        if not all([m.metadata.bind for m in models + (model,)]):
            return None

        if not all([model.metadata.bind == m.metadata.bind for m in models]):
            raise HeterogenuousEngineError

        return sessionmaker(bind=model.metadata.bind)()
