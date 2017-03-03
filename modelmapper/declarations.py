from collections import namedtuple


class Field(namedtuple('Field', 'origin_access destination_access name validator')):

    __slots__ = ()

    def __new__(cls, origin_access, destination_access, name=None, validator=None):
        return super(Field, cls).__new__(cls, origin_access, destination_access, name, validator)


class Mapper(namedtuple('Mapper', 'origin_access destination_access mapper name validator')):

    __slots__ = ()

    def __new__(cls, origin_access, destination_access, mapper, name=None, validator=None):
        return super(Mapper, cls).__new__(cls, origin_access, destination_access, mapper, name, validator)


class UniformMapper(Mapper): pass


class ListMapper(Mapper): pass


class CombinedField(object):

    def __init__(self, *field_accesses, **info):
        self.field_accesses = field_accesses
        self.name = info.get('name', '')
        self.validator = info.get('validator', '')
        self._fields = None

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, val):
        self._fields = val
