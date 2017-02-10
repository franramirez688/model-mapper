from modelmapper.accessors import ModelAccessor
from modelmapper.core import ModelMapper, Mapper, UniformMapper, ListMapper


Field = namedtuple('Field', 'origin_access destination_access name validator')
Mapper = namedtuple('Mapper', Field._fields + ('mapper',))
ListMapper = namedtuple('ListMapper', Mapper._fields)
UniformMapper = namedtuple('UniformMapper', Mapper._fields)


class IntegrationsModelMapper(ModelMapper):

    def __init__(self, origin_model, destination_model, mapper, meta_info):
        super(IntegrationsModelMapper, self).__init__(origin_model, destination_model, mapper)
        self._listener = QListener()

        self._meta_info = meta_info
        self._meta_info_accessor = ModelAccessor

    def _prepare_mapper_and_get_new_mappers(self):
        children_declarations = self._children_declarations
        create_child_by_declaration = self.create_child_by_declaration_type

        for link_name, declaration_type in self._mapper_accessor.iteritems():
            if isinstance(declaration_type, (Mapper, UniformMapper, ListMapper)):
                model_mapper = create_child_by_declaration(declaration_type)
                children_declarations.add((declaration_type[0], declaration_type[1], model_mapper))
                yield link_name, model_mapper
            elif isinstance(declaration_type, CombinedLinks):
                relations = [self._mapper_accessor[access] for access in declaration_type.relations]
                self._listener.append_relations(declaration_type.accessor, relations)
            else:
                dest.parent_accessor = self._dest_accessor
                self._listener.append(dest)

    def prepare_mapper(self):
        mapper = self._mapper_accessor
        new_model_mappers = self._prepare_mapper_and_get_new_mappers() or []

        for (link_name, model_mapper) in new_model_mappers:
            mapper[link_name] = model_mapper
            mapper[link_name].prepare_mapper()
