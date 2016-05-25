""":mod:`news.backends.sqlalchemy` --- Backend SQLAlchemy implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides an implementation of news backend for SQLAlchemy.

"""
from sqlalchemy.orm import sessionmaker
from .abstract import AbstractBackend
from ..exceptions import HeterogenuousEngineError


class SQLAlchemyBackend(AbstractBackend):
    def __init__(self, bind=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # use given session if available. otherwise try to retrieve session
        # from the engine bound to models if exists.
        self.session = bind or self._retrieve_session(self.Schedule, self.News)

    def get_news(self, id):
        if not id:
            return None
        else:
            return self.session.query(self.News).get(id)

    def get_news_by(self, owner, url):
        if not owner or not url:
            return None

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
        try:
            root = [n for n in news if n.is_root][0]
        except IndexError:
            root = None

        if root:
            # save-update cascade will do heavy lifting
            self.session.add(root)
            self.session.commit()

    def delete_news(self, *news):
        self.session.delete(*news)
        self.session.commit()

    def get_schedule(self, id):
        return self.session.query(self.Schedule).get(id)

    def get_schedules(self, owner=None, url=None):
        query = self.session.query(self.Schedule)

        if owner:
            query = query.filter(self.Schedule.owner == owner)
        if url:
            query = query.filter(self.Schedule.url == url)

        return query.all()

    def bind(self, session):
        self.session = session
        return self

    @staticmethod
    def _retrieve_session(model, *models):
        if not all([m.metadata.bind for m in models + (model,)]):
            return None

        if not all([model.metadata.bind == m.metadata.bind for m in models]):
            raise HeterogenuousEngineError

        return sessionmaker(bind=model.metadata.bind)()
