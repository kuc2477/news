import abc
from cached_property import cached_property
from extraction import Extractor
from ..utils import url


# =======================
# Common model base class
# =======================

class NewsModel(object):
    pass


# =============================
# Generic abstract model mixins
# =============================

class AbstractModelMixinBase(object):
    @abc.abstractmethod
    def get_id(self):
        return NotImplemented


# ==========================
# News abstract model mixins
# ==========================

class AbstractOwnerMixin(AbstractModelMixinBase):
    pass


class AbstractScheduleMetaMixin(AbstractModelMixinBase):
    @abc.abstractmethod
    def get_owner(self):
        return NotImplemented

    @abc.abstractmethod
    def get_url(self):
        return NotImplemented

    @abc.abstractmethod
    def get_cycle(self):
        return NotImplemented

    @abc.abstractmethod
    def get_filter_options(self):
        return NotImplemented


class AbstractNewsMixin(AbstractModelMixinBase):
    @abc.abstractclassmethod
    def create_instance(self, root, url, content, owner=None, src=None):
        return NotImplemented

    @abc.abstractmethod
    def get_owner(self):
        return NotImplemented

    @abc.abstractmethod
    def get_root(self):
        return NotImplemented

    @abc.abstractmethod
    def get_src(self):
        return NotImplemented

    @abc.abstractmethod
    def get_url(self):
        return NotImplemented

    @abc.abstractmethod
    def get_title(self):
        return NotImplemented

    @abc.abstractmethod
    def get_content(self):
        return NotImplemented

    @abc.abstractmethod
    def get_description(self):
        return NotImplemented

    @abc.abstractmethod
    def get_image(self):
        return NotImplemented

    @property
    def depth(self):
        return url.depth(self.get_root().get_url(), self.get_url())

    @property
    def distance(self):
        return 0 if not self.get_src() else self.get_src().distance + 1

    @cached_property
    def extracted(self):
        return Extractor().extract(self.content)

    @property
    def title(self):
        return self.extracted.title

    @property
    def image(self):
        return self.extracted.image

    @property
    def description(self):
        return self.extracted.description


# =====================
# Model base generators
# =====================

def getModelABCMetaClass(orm_model_base, meta=False):
    orm_model_metaclass = type(orm_model_base) if not meta else orm_model_base

    return type(
        'ABC{}'.format(orm_model_metaclass.__name__),
        (abc.ABCMeta, orm_model_metaclass), {})


def getModelBase(orm_model_base, abstract_model_mixin,
                 meta=False, name='Base'):
    metaclass = getModelABCMetaClass(orm_model_base, meta)
    attr_dict = {'__metaclass__': metaclass}
    return type(name, (abstract_model_mixin, NewsModel), attr_dict)
