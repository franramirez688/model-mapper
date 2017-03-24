import itertools

from modelmapper import exceptions as exc, compat
from modelmapper.accessors import ModelAccessor, FieldAccessor
from modelmapper.declarations import Mapper, UniformMapper, ListMapper, CombinedField


class ModelMapper(object):
    """Linker class between an origin model and a destination one
    """

    def __init__(self, origin_model, destination_model, mapper, **info):
        self._origin_model = origin_model if origin_model is None else dict()
        self._destination_model = destination_model
        self._mapper = mapper  # MutableMapping()

        self._mapper_accessor = ModelAccessor(mapper)
        self._origin_accessor = ModelAccessor(origin_model)
        self._destination_accessor = ModelAccessor(destination_model)

        # Variable to record tuple(orig_access, dest_access, model_mapper_obj)
        self._children = set()  # set([(link_name, <obj ModelMapper>),])
        self._fields = set()  # set([(link_name, <obj ModelMapper>),])
        self._combined_fields = set()  # set([(link_name, <obj ModelMapper>),])

        self._info = ModelAccessor(info)

    def create_child_by_declaration_type(self, declaration):

        def _get_complete_info_and_parent_models():
            info = declaration.info
            orig_access = declaration.origin_access
            dest_access = declaration.destination_access

            info['origin_access'] = orig_access
            info['destination_access'] = dest_access

            orig_model = self._origin_accessor.get(orig_access) if orig_access else self._origin_accessor.model
            dest_model = self._destination_accessor.get(dest_access) if dest_access \
                                                                     else self._destination_accessor.model

            return info, orig_model, dest_model

        mapper = declaration.mapper
        info, orig_model, dest_model = _get_complete_info_and_parent_models()

        if isinstance(declaration, UniformMapper):
            return UniformListModelMapper(orig_model, dest_model, mapper, **info)
        elif isinstance(declaration, Mapper):
            return ModelMapper(orig_model, dest_model, mapper, **info)

    @property
    def origin_model(self):
        return self._origin_model

    @origin_model.setter
    def origin_model(self, val):
        self._origin_model = val
        self._origin_accessor = ModelAccessor(val)

        for _, model_mapper in self._children:
            model_mapper.origin_model = self._origin_accessor[model_mapper.origin_access]

    @property
    def destination_model(self):
        return self._destination_model

    @destination_model.setter
    def destination_model(self, val):
        self._destination_model = val
        self._destination_accessor = ModelAccessor(val)

        for _, model_mapper in self._children:
            model_mapper.destination_model = self._destination_accessor[model_mapper.destination_access]

    @property
    def info(self):
        return self._info

    @property
    def origin_access(self):
        return self._info.get('origin_access')

    @property
    def destination_access(self):
        return self._info.get('destination_access')

    @property
    def mapper(self):
        return self._mapper

    @mapper.setter
    def mapper(self, val):
        self._mapper = val
        self._mapper_accessor = ModelAccessor(val)

    @property
    def origin_accessor(self):
        return self._origin_accessor

    @property
    def destination_accessor(self):
        return self._destination_accessor

    @property
    def mapper_accessor(self):
        return self._mapper_accessor

    @property
    def children(self):
        return self._children

    @property
    def fields(self):
        return self._fields

    @property
    def combined_fields(self):
        return self._combined_fields

    def prepare_mapper(self):
        _add_children = self._children.add
        _add_field = self._fields.add
        _add_combined_field = self._combined_fields.add
        create_child_by_declaration = self.create_child_by_declaration_type
        new_links = dict()

        for link_name, declaration_type in self._mapper_accessor:
            if isinstance(declaration_type, (Mapper, UniformMapper, ListMapper)):
                model_mapper = create_child_by_declaration(declaration_type)
                new_links[link_name] = model_mapper
                model_mapper.prepare_mapper()
                _add_children((link_name, model_mapper))
            elif isinstance(declaration_type, CombinedField):
                declaration_type.init_nested_fields(self)
                _add_combined_field((link_name, declaration_type))
            else:
                _add_field((link_name, declaration_type))

        # Update mapper model to change Mapper declarations to ModelMapper classes
        self._mapper_accessor.model.update(new_links)

    def destination_to_origin(self):
        orig_accessor = self._origin_accessor
        dest_accessor = self._destination_accessor

        for _, child in self._children:
            child.destination_to_origin()

        for _, field in self._fields:
            orig_access = field[0]
            dest_access = field[1]
            try:
                dest_field_value = dest_accessor[dest_access]
            except exc.ModelAccessorAttributeError:
                pass
            else:
                orig_accessor[orig_access] = dest_field_value

    def origin_to_destination(self):
        orig_accessor = self._origin_accessor
        dest_accessor = self._destination_accessor

        for _, child in self._children:
            child.origin_to_destination()

        for _, field in self._fields:
            orig_access = field[0]
            dest_access = field[1]
            try:
                orig_field_value = orig_accessor[orig_access]
            except exc.ModelAccessorAttributeError:
                pass
            else:
                dest_accessor[dest_access] = orig_field_value

    def to_dict(self, only_origin=False, only_destination=False):
        dest_accessor = self._destination_accessor
        orig_accessor = self._origin_accessor
        ret = {}

        for link_name, link_value in self._mapper_accessor:
            if isinstance(link_value, ModelMapper):
                ret[link_name] = link_value.to_dict(only_origin=only_origin, only_destination=only_destination)
            elif only_origin:
                ret[link_name] = orig_accessor[link_value[0]]
            elif only_destination:
                ret[link_name] = dest_accessor[link_value[1]]
            else:
                ret[link_name] = (orig_accessor[link_value[0]], dest_accessor[link_value[1]])
        return ret

    def _filter_fields_by_access(self, access, field_index):

        def compare_access(decl):
            orig_or_dest = decl[1][field_index]  # (link_name, Field)
            orig_or_dest_access = orig_or_dest.access if isinstance(orig_or_dest, FieldAccessor) else orig_or_dest
            return access == orig_or_dest_access

        return compat.filter(compare_access, self._fields)

    def filter_fields_by_orig_access(self, access):
        return self._filter_fields_by_access(access, 0)

    def filter_fields_by_dest_access(self, access):
        return self._filter_fields_by_access(access, 1)

    def filter_children_by_orig_access(self, access):
        return compat.filter(lambda decl: access == decl[1].origin_access,  # (link_name, ModelMapper)
                             self._children)

    def filter_children_by_dest_access(self, access):
        return compat.filter(lambda decl: access == decl[1].destination_access,
                             self._children)

    def filter_origin_access(self, access):
        return itertools.chain(self.filter_children_by_orig_access(access),
                               self.filter_fields_by_orig_access(access))

    def filter_destination_access(self, access):
        return itertools.chain(self.filter_children_by_dest_access(access),
                               self.filter_fields_by_dest_access(access))

    def __getitem__(self, item):
        return self._mapper_accessor[item]

    def __setitem__(self, key, value):
        self._mapper_accessor[key] = value

    def __iter__(self):
        return iter(self._mapper_accessor)

    __getattr__ = __getitem__  # If getattr(self, 'link')


# TODO: At this moment is only possible to be the origin a list


class UniformListModelMapper(ModelMapper):

    def __init__(self, origin_model, destination_model, mapper, **info):
        assert isinstance(origin_model, list), "Origin model must be a list with uniform data"

        self._orig_data = origin_model or []
        self._index = 0
        origin_model = origin_model[0] if len(origin_model) > 0 else dict()
        super(UniformListModelMapper, self).__init__(origin_model, destination_model, mapper, **info)

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

        for _, model_mapper in self._children:
            model_mapper.origin_model = self._origin_accessor[model_mapper.origin_access]

    def origin_to_destination(self):
        if not self._orig_data:
            return
        super(UniformListModelMapper, self).origin_to_destination()

    def insert_data(self, data_model=None, index=-1):
        data_model = dict() if data_model is None else data_model
        self.orig_data.insert(index, data_model)

    def delete_data(self, index=-1):
        try:
            self.orig_data.pop(index)
        except IndexError:
            raise exc.ModelMapperError("The index {} is out of range".format(index))

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        try:
            self._update_index(index)
            self.origin_to_destination()
        except IndexError:
            raise exc.ModelMapperError("The index {} is out of range".format(index))

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

        for link_name, link_value in self._mapper_accessor:
            for index, _ in enumerate(model):
                update_index(index)
                if isinstance(link_value, ModelMapper):
                    ret[index][link_name] = link_value.to_dict(only_origin=True)
                else:
                    ret[index][link_name] = self._origin_accessor[link_value[0]]
        update_index(current_index)
        return ret


# TODO: ModelMapper to make relations between origin/destination lists models
#
# class ListModelMapper(ModelMapper):
#
#     LINK = '[{}].{}'
#
#     def __init__(self, origin_model, destination_model, mapper, info=info):
#         origin_model = origin_model if origin_model is None else list()
#         super(ListModelMapper, self).__init__(origin_model, destination_model, mapper, info=info)
#
#     def _values_updater(self, func_name, accessor_to_set, accessor_to_get, setter_index, getter_index):
#         link = ListModelMapper.LINK.format
#
#         for _, link_value in self._mapper_accessor:
#             for index, _ in enumerate(accessor_to_get.model):
#                 if isinstance(link_value, ModelMapper):
#                     orig_to_dest_or_vice_versa = getattr(link_value, func_name)
#                     orig_to_dest_or_vice_versa()
#                 else:
#                     item_to_set = link(index, link_value[setter_index])
#                     item_to_get = link(index, link_value[getter_index])
#                     try:
#                         accessor_to_set[item_to_set] = accessor_to_get[item_to_get]
#                     except exc.ModelAccessorAttributeError:
#                         pass
#
#     def to_dict(self, only_origin=False, only_destination=False):
#         if only_origin:
#             return self._to_dict_only_origin()
#         elif only_destination:
#             return self._to_dict_only_destination()
#         else:
#             return (self._to_dict_only_origin(), self._to_dict_only_destination())
#
#     def _to_dict_only_destination(self):
#         dest_accessor = self._destination_accessor
#         model = self._destination_model
#         ret = [dict() for _ in range(len(model))]
#         link = ListModelMapper.LINK.format
#
#         for link_name, link_value in self._mapper_accessor:
#             for index, _ in enumerate(model):
#                 if isinstance(link_value, ModelMapper):
#                     ret[index][link_name] = link_value.to_dict(only_destination=True)
#                 else:
#                     ret[index][link_name] = dest_accessor[link(index, link_value[1])]
#         return ret
#
#     def _to_dict_only_origin(self):
#         orig_accessor = self._origin_accessor
#         model = self._origin_model
#         ret = [dict() for _ in range(len(model))]
#         link = ListModelMapper.LINK.format
#
#         for link_name, link_value in self._mapper_accessor:
#             for index, _ in enumerate(model):
#                 if isinstance(link_value, ModelMapper):
#                     ret[index][link_name] = link_value.to_dict(only_origin=True)
#                 else:
#                     ret[index][link_name] = orig_accessor[link(index, link_value[0])]
#         return ret
