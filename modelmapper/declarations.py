from collections import namedtuple

from modelmapper.exceptions import DeclarationError


class Field(namedtuple('Field', 'origin_access destination_access info')):

    __slots__ = ()

    def __new__(cls, origin_access, destination_access, info=None):
        info = info or dict(name=None, validator=None, help_text=None)
        return super(Field, cls).__new__(cls, origin_access, destination_access, info)

    def __getattr__(self, item):
        try:
            return self.info[item]
        except KeyError:
            raise DeclarationError("This attribute has not been defined in Field declaration")


class Mapper(namedtuple('Mapper', 'origin_access destination_access mapper info')):

    __slots__ = ()

    def __new__(cls, origin_access, destination_access, mapper, info=None):
        info = info or dict(name=None, validator=None, help_text=None)
        return super(Mapper, cls).__new__(cls, origin_access, destination_access, mapper, info)

    def __getattr__(self, item):
        try:
            return self.info[item]
        except KeyError:
            raise DeclarationError("This attribute has not been defined in "
                                   "{class_name} declaration".format(class_name=self.__class__.__name__))


class UniformMapper(Mapper):
    pass


class ListMapper(Mapper):
    pass


class CombinedField(object):

    def __init__(self, *nested_accesses, **info):
        self.nested_accesses = nested_accesses
        self.info = info
        self._nested_fields = set()

    def __getattr__(self, item):
        try:
            return self.info[item]
        except KeyError:
            raise DeclarationError("This attribute has not been defined in CombinedField declaration")

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
