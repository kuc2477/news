import abc


class ModelBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def from_domain(self, domain_object):
        return NotImplemented

    @abc.abstractmethod
    def to_domain(self):
        return NotImplemented
