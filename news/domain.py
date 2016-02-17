import abc


class DomainBase(metaclass=abc.ABCMeta):
    """
    Domain base class that should be implemented by domain classes.

    Provide common attributes and properties to help persistance between domain
    objects and a news store backend models.

    """

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        template = 'Domain{0}: {1}'
        return template.format(type(self).__name__, self.id)

    @abc.abstractproperty
    def id(self):
        """
        Identifier to check equality between domain objects.

        Note that this has nothing to do with `id` or `primary key` of store
        backend model instances except for the fact that it can be used as
        domain identifier.

        """
        return NotImplemented

    @abc.abstractproperty
    def serialized(self):
        return NotImplemented

    @classmethod
    def from_model(cls, model):
        return model.to_domain()

    def to_model(self, model_class):
        return model_class.from_domain(self)
