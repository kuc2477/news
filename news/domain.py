import abc


class DomainBase(metaclass=abc.ABCMeta):
    """
    Base class that should be implemented by domain classes. Provides
    common interface for domain classes.

    """

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    @abc.abstractmethod
    def __str__(self):
        return NotImplemented

    @abc.abstractproperty
    def id(self):
        return NotImplemented

    @abc.abstractproperty
    def serialized(self):
        return NotImplemented
