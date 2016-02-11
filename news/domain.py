import abc


class DomainBase(metaclass=abc.ABCMeta):
    """
    Domain base class that should be implemented by domain classes.

    Provide common attributes and properties for persistance between domain
    objects and a store backend.

    """

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        template = '{0}: {1}'.format()
        return self.id

    @abc.abstractproperty
    def id(self):
        return NotImplemented

    @abc.abstractproperty
    def serialized(self):
        return NotImplemented
