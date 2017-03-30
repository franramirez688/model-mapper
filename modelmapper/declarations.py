from modelmapper.exceptions import DeclarationError


class _UtilsMixin(object):
    __slots__ = ('info',)

    def __getattr__(self, item):
        try:
            return self.info[item]
        except KeyError:
            raise DeclarationError("{item} has not been defined in 'info' variable of"
                                   "{class_name} declaration".format(item=item,
                                                                     class_name=self.__class__.__name__))


class Field(_UtilsMixin):
    __slots__ = ('origin_access', 'destination_access')

    def __init__(self, origin_access, destination_access, **info):
        self.origin_access = origin_access
        self.destination_access = destination_access
        self.info = info


class Mapper(_UtilsMixin):
    __slots__ = ('origin_access', 'destination_access', 'mapper')

    def __init__(self, origin_access, destination_access, mapper, **info):
        self.origin_access = origin_access
        self.destination_access = destination_access
        self.mapper = mapper
        self.info = info


class UniformMapper(Mapper):
    __slots__ = ()


class ListMapper(Mapper):
    __slots__ = ()


class CombinedField(_UtilsMixin):
    __slots__ = ('nested_accesses', 'nested_fields')

    def __init__(self, *nested_accesses, **info):
        self.nested_accesses = nested_accesses
        self.info = info
        self.nested_fields = set()

    @property
    def nested_orig_accesses(self):
        return (field.origin_access for field in self.nested_fields if isinstance(field, (Field, tuple)))

    @property
    def nested_dest_accesses(self):
        return (field.destination_access for field in self.nested_fields if isinstance(field, (Field, tuple)))

    def init_nested_fields(self, model_accessor):
        self.nested_fields = set([model_accessor[access] for access in self.nested_accesses])
