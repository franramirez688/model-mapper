from collections import namedtuple

from modelmapper.core import ModelMapper


Field = namedtuple('Field', 'origin_access destination_access name validator')
Mapper = namedtuple('Mapper', 'origin_access destination_access mapper name validator')
ListMapper = namedtuple('ListMapper', Mapper._fields)
UniformMapper = namedtuple('UniformMapper', Mapper._fields)


class CombinedField(object):

    def __int__(self, name, validator, relations=None):
        self.name = name
        self.validator = validator
        self.relations = relations


class IntegrationsModelMapper(ModelMapper):

    def __init__(self, origin_model, destination_model, mapper, listener=None):
        super(IntegrationsModelMapper, self).__init__(origin_model, destination_model, mapper)
        self._listener = listener

    def _prepare_mapper_and_get_new_mappers(self):
        children_declarations = self._children_declarations
        create_child_by_declaration = self.create_child_by_declaration_type

        for link_name, declaration_type in self._mapper_accessor.iteritems():
            if isinstance(declaration_type, (Mapper, UniformMapper, ListMapper)):
                model_mapper = create_child_by_declaration(declaration_type)
                children_declarations.add((declaration_type[0], declaration_type[1], model_mapper))
                yield link_name, model_mapper
            elif isinstance(declaration_type, CombinedField):
                relations = [self._mapper_accessor[access] for access in declaration_type.relations]
                self._listener.append_combined(declaration_type.access, relations)
            else:
                dest = declaration_type[1]
                dest.parent_accessor = self._dest_accessor
                self._listener.append(dest)

    def prepare_mapper(self):
        mapper = self._mapper_accessor
        new_model_mappers = self._prepare_mapper_and_get_new_mappers() or []

        for (link_name, model_mapper) in new_model_mappers:
            mapper[link_name] = model_mapper
            mapper[link_name].prepare_mapper()

    def map_errors(self, errors):
        ret = []
        for origin_access, error in errors:
            declaration_type = self._mapper_accessor.get(origin_access)
            if declaration_type is None:
                continue
            if isinstance(declaration_type, ModelMapper):
                ret.append(declaration_type.name)
                ret.append(declaration_type.map_and_render(error))
            elif isinstance(declaration_type, CombinedField):
                ret.append((declaration_type.name, error))
            elif isinstance(declaration_type, (Field, tuple)):
                ret.append((declaration_type[3], error, declaration_type[1]))
        return ret
