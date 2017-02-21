from modelmapper import exceptions
from modelmapper.accessors import ModelAccessor, ModelDictAccessor
from modelmapper.declarations import Mapper, UniformMapper, ListMapper, CombinedField, Field
from modelmapper.qt.fields import QWidgetAccessor
from modelmapper.qt.listener import Listener


_listener = Listener()


class ModelMapper(object):
    """Linker class between an origin model and a destination one
    """

    def __init__(self, origin_model, destination_model, mapper):
        self._origin_model = origin_model if origin_model is None else dict()
        self._destination_model = destination_model
        self._mapper = mapper  # MutableMapping()

        self._mapper_accessor = ModelDictAccessor(mapper)
        self._origin_accessor = ModelAccessor(origin_model)
        self._destination_accessor = ModelAccessor(destination_model)

        # Variable to record tuple(orig_access, dest_access, model_mapper_obj)
        self._children_declarations = set()

    @staticmethod
    def factory(orig_model, dest_model, mapper):
        if isinstance(orig_model, list) and isinstance(dest_model, list):
            return ListModelMapper(orig_model, dest_model, mapper)
        elif isinstance(orig_model, list) or isinstance(dest_model, list):
            return UniformListModelMapper(orig_model, dest_model, mapper)
        else:
            return ModelMapper(orig_model, dest_model, mapper)

    def create_child_by_declaration_type(self, declaration):
        orig_access = declaration.origin_access
        dest_access = declaration.destination_access
        mapper = declaration.mapper

        orig_model = self._origin_accessor.get(orig_access) if orig_access else self._origin_accessor.model
        dest_model = self._destination_accessor.get(dest_access) if dest_access else self._destination_accessor.model

        if isinstance(declaration, ListMapper):
            return ListModelMapper(orig_model, dest_model, mapper)
        elif isinstance(declaration, UniformMapper):
            return UniformListModelMapper(orig_model, dest_model, mapper)
        elif isinstance(declaration, Mapper):
            return ModelMapper(orig_model, dest_model, mapper)

    @property
    def origin_model(self):
        return self._origin_model

    @origin_model.setter
    def origin_model(self, val):
        self._origin_model = val
        self._origin_accessor = ModelAccessor(val)

        for orig_access, _, model_mapper in self._children_declarations:
            model_mapper.origin_model = self._origin_accessor[orig_access]

    @property
    def destination_model(self):
        return self._destination_model

    @destination_model.setter
    def destination_model(self, val):
        self._destination_model = val
        self._destination_accessor = ModelAccessor(val)

        for _, dest_access, model_mapper in self._children_declarations:
            model_mapper.destination_model = self._destination_accessor[dest_access]

    @property
    def mapper(self):
        return self._mapper

    @mapper.setter
    def mapper(self, val):
        self._mapper = val
        self._mapper_accessor = ModelDictAccessor(val)

    @property
    def origin_accessor(self):
        return self._origin_accessor

    @property
    def destination_accessor(self):
        return self._destination_accessor

    @property
    def mapper_accessor(self):
        return self._mapper_accessor

    def prepare_fields(self):
        for link_name, declaration_type in self._mapper_accessor.iteritems():
            if isinstance(declaration_type, (ModelMapper)):
                declaration_type.prepare_fields()
            elif isinstance(declaration_type, CombinedField):
                declarations = set([self._mapper_accessor[access] for access in declaration_type.field_accesses])
                accessors = set([decl[1] for decl in declarations if isinstance(decl, (Field, tuple))])
                _listener.add_combined_fields(accessors, declaration_type.validator)
            elif isinstance(declaration_type[1], QWidgetAccessor):
                dest_accessor = declaration_type[1]
                dest_accessor.parent_accessor = self._destination_accessor
                dest_accessor.validator = declaration_type[3] if len(declaration_type) > 3 else None
                dest_accessor.connect_signals()

    def _prepare_mapper_and_get_new_mappers(self):
        children_declarations = self._children_declarations
        create_child_by_declaration = self.create_child_by_declaration_type

        for link_name, declaration_type in self._mapper_accessor.iteritems():
            if isinstance(declaration_type, (Mapper, UniformMapper, ListMapper)):
                model_mapper = create_child_by_declaration(declaration_type)
                children_declarations.add((declaration_type[0], declaration_type[1], model_mapper))
                yield link_name, model_mapper

    def prepare_mapper(self):
        mapper = self._mapper_accessor
        new_model_mappers = self._prepare_mapper_and_get_new_mappers() or []

        for (link_name, model_mapper) in new_model_mappers:
            mapper[link_name] = model_mapper
            mapper[link_name].prepare_mapper()

    def _values_updater(self, func_name, accessor_to_set, accessor_to_get, setter_index, getter_index):
        for _, link_value in self._mapper_accessor.iteritems():
            if isinstance(link_value, ModelMapper):
                orig_to_dest_or_vice_versa = getattr(link_value, func_name)
                orig_to_dest_or_vice_versa()
            elif isinstance(link_value, (Field, tuple)):
                item_to_set = link_value[setter_index]
                item_to_get = link_value[getter_index]
                try:
                    accessor_to_set[item_to_set] = accessor_to_get[item_to_get]
                except exceptions.ModelAccessorAttributeError:
                    pass

    def destination_to_origin(self):
        self._values_updater('destination_to_origin', self._origin_accessor, self._destination_accessor, 0, 1)

    def origin_to_destination(self):
        self._values_updater('origin_to_destination', self._destination_accessor, self._origin_accessor, 1, 0)

    def to_dict(self, only_origin=False, only_destination=False):
        dest_accessor = self._destination_accessor
        orig_accessor = self._origin_accessor
        ret = {}

        for link_name, link_value in self._mapper_accessor.iteritems():
            if isinstance(link_value, ModelMapper):
                ret[link_name] = link_value.to_dict(only_origin=only_origin, only_destination=only_destination)
            elif only_origin:
                ret[link_name] = orig_accessor[link_value[0]]
            elif only_destination:
                ret[link_name] = dest_accessor[link_value[1]]
            else:
                ret[link_name] = (orig_accessor[link_value[0]], dest_accessor[link_value[1]])
        return ret

    def __getitem__(self, item):
        return self._mapper_accessor[item]

    def __setitem__(self, key, value):
        self._mapper_accessor[key] = value

    __getattr__ = __getitem__  # If getattr(self, 'link')


# TODO: At this moment is only possible to be the origin a list


class UniformListModelMapper(ModelMapper):

    def __init__(self, origin_model, destination_model, mapper):
        assert isinstance(origin_model, list), "Origin model must be a list with uniform data"

        self._orig_data = origin_model or []
        self._index = 0
        origin_model = origin_model[0] if len(origin_model) > 0 else dict()
        super(UniformListModelMapper, self).__init__(origin_model, destination_model, mapper)

    @property
    def orig_data(self):
        return self._orig_data

    @orig_data.setter
    def orig_data(self, value):
        self._orig_data = value

    @ModelMapper.origin_model.setter
    def origin_model(self, val):
        self._orig_data = val
        self._origin_model = val[self._index]
        self._origin_accessor = ModelAccessor(self._origin_model)

        for orig_access, _, model_mapper in self._children_declarations:
            model_mapper.origin_model = self._origin_accessor[orig_access]

    def origin_to_destination(self):
        if not self._orig_data:
            return
        self._values_updater('origin_to_destination', self._destination_accessor, self._origin_accessor, 1, 0)

    def insert_data(self, data_model=None, index=-1):
        data_model = dict() if data_model is None else data_model
        self.orig_data.insert(index, data_model)

    def delete_data(self, index=-1):
        try:
            self.orig_data.pop(index)
        except IndexError:
            raise exceptions.ModelMapperError("The index {} is out of range".format(index))

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        try:
            self._update_index(index)
            self.origin_to_destination()
        except IndexError:
            raise exceptions.ModelMapperError("The index {} is out of range".format(index))

    def _update_index(self, index):
        if self._index == index:
            return
        self._index = index
        self._origin_model = self._orig_data[index]
        self._origin_accessor = ModelAccessor(self._origin_model)
        # Calling to parent's origin_model setter
        ModelMapper.origin_model.fset(self, self._origin_model)

    def to_dict(self, only_origin=False, only_destination=False):
        if only_origin:
            return self._to_dict_only_origin()
        elif only_destination:
            return super(UniformListModelMapper, self).to_dict(only_destination=True)
        else:
            return (self._to_dict_only_origin(), super(UniformListModelMapper, self).to_dict(only_destination=True))

    def _to_dict_only_origin(self):
        update_index = self._update_index
        model = self._orig_data
        ret = [dict() for _ in range(len(model))]
        current_index = self._index

        for link_name, link_value in self._mapper_accessor.iteritems():
            for index, _ in enumerate(model):
                update_index(index)
                if isinstance(link_value, ModelMapper):
                    ret[index][link_name] = link_value.to_dict(only_origin=True)
                else:
                    ret[index][link_name] = self._origin_accessor[link_value[0]]
        update_index(current_index)
        return ret


class ListModelMapper(ModelMapper):

    LINK = '[{}].{}'

    def __init__(self, origin_model, destination_model, mapper):
        origin_model = origin_model if origin_model is None else list()
        super(ListModelMapper, self).__init__(origin_model, destination_model, mapper)

    def _values_updater(self, func_name, accessor_to_set, accessor_to_get, setter_index, getter_index):
        link = ListModelMapper.LINK.format

        for _, link_value in self._mapper_accessor.iteritems():
            for index, _ in enumerate(accessor_to_get.model):
                if isinstance(link_value, ModelMapper):
                    orig_to_dest_or_vice_versa = getattr(link_value, func_name)
                    orig_to_dest_or_vice_versa()
                else:
                    item_to_set = link(index, link_value[setter_index])
                    item_to_get = link(index, link_value[getter_index])
                    try:
                        accessor_to_set[item_to_set] = accessor_to_get[item_to_get]
                    except exceptions.ModelAccessorAttributeError:
                        pass

    def to_dict(self, only_origin=False, only_destination=False):
        if only_origin:
            return self._to_dict_only_origin()
        elif only_destination:
            return self._to_dict_only_destination()
        else:
            return (self._to_dict_only_origin(), self._to_dict_only_destination())

    def _to_dict_only_destination(self):
        dest_accessor = self._destination_accessor
        model = self._destination_model
        ret = [dict() for _ in range(len(model))]
        link = ListModelMapper.LINK.format

        for link_name, link_value in self._mapper_accessor.iteritems():
            for index, _ in enumerate(model):
                if isinstance(link_value, ModelMapper):
                    ret[index][link_name] = link_value.to_dict(only_destination=True)
                else:
                    ret[index][link_name] = dest_accessor[link(index, link_value[1])]
        return ret

    def _to_dict_only_origin(self):
        orig_accessor = self._origin_accessor
        model = self._origin_model
        ret = [dict() for _ in range(len(model))]
        link = ListModelMapper.LINK.format

        for link_name, link_value in self._mapper_accessor.iteritems():
            for index, _ in enumerate(model):
                if isinstance(link_value, ModelMapper):
                    ret[index][link_name] = link_value.to_dict(only_origin=True)
                else:
                    ret[index][link_name] = orig_accessor[link(index, link_value[0])]
        return ret
