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

    def __init__(self, *nested_accesses, **info):
        self.nested_accesses = nested_accesses
        self.name = info.get('name', '')
        self.validator = info.get('validator', '')
        self._nested_fields = set()

    @property
    def nested_fields(self):
        return self._nested_fields

    @nested_fields.setter
    def nested_fields(self, val):
        self._nested_fields = val

    def nested_orig_accesses(self):
        return (field[0] for field in self.nested_fields if isinstance(field, (Field, tuple)))

    def nested_dest_accesses(self):
        return (field[1] for field in self.nested_fields if isinstance(field, (Field, tuple)))

    def init_nested_fields(self, model_accessor):
        self.nested_fields = set([model_accessor[access] for access in self.nested_accesses])
