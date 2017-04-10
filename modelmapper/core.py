import itertools

from modelmapper import exceptions as exc, compat
from modelmapper.accessors import ModelAccessor, FieldAccessor
from modelmapper.declarations import Mapper, UniformMapper, ListMapper, CombinedField


class ModelMapper(object):
    """Main class to make the mapping and linking between an origin model and a
    destination model
    """
    __slots__ = ('_origin_model', '_destination_model', '_mapper', '_mapper_accessor',
                 '_origin_accessor', '_destination_accessor', '_children', '_fields',
                 '_combined_fields', '_info')

    def __init__(self, origin_model, destination_model, mapper, **info):
        """
        :param origin_model: any object
        :param destination_model: any object
        :param mapper: :class:`dict` object with mapping info
        :param info: any additional kwargs information
        """
        self._origin_model = dict() if origin_model is None else origin_model
        self._destination_model = dict() if destination_model is None else destination_model
        self._mapper = mapper  # MutableMapping()

        self._mapper_accessor = ModelAccessor(mapper)
        self._origin_accessor = ModelAccessor(origin_model)
        self._destination_accessor = ModelAccessor(destination_model)

        # Variable to record tuple(orig_access, dest_access, model_mapper_obj)
        self._children = set()  # set([(field_name, <obj ModelMapper>),])
        self._fields = set()  # set([(field_name, <obj ModelMapper>),])
        self._combined_fields = set()  # set([(field_name, <obj ModelMapper>),])

        self._info = ModelAccessor(info)

    def create_child_by_declaration_type(self, declaration):
        """Create a new :class:`ModelMapper` object, based on a
        :class:`Mapper` declaration

        :param declaration: :class:`Mapper`
        :return: :class:`ModelMapper`
        """

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
        """Prepare the original mapper dictionary ``mapper`` and transform it,
        converting :class:`Mapper` to :class:`ModelMapper`.

        Here, it's saved all the model-mapper :class:`Field`, :class:`CombinedField`
        and :class:`ModelMapper`
        :return: None
        """
        _add_children = self._children.add
        _add_field = self._fields.add
        _add_combined_field = self._combined_fields.add
        create_child_by_declaration = self.create_child_by_declaration_type
        updated_fields = dict()

        for field_name, declaration_type in self._mapper_accessor:
            if isinstance(declaration_type, (Mapper, UniformMapper, ListMapper)):
                model_mapper = create_child_by_declaration(declaration_type)
                updated_fields[field_name] = model_mapper
                model_mapper.prepare_mapper()
                _add_children((field_name, model_mapper))
            elif isinstance(declaration_type, CombinedField):
                _add_combined_field((field_name, declaration_type))
            else:
                _add_field((field_name, declaration_type))

        # Update mapper model to change Mapper declarations to ModelMapper classes
        self._mapper_accessor.model.update(updated_fields)

    def destination_to_origin(self, field_name=None):
        """Update all the values, or some specific value from a field, from
        destination model to origin one

        :param field_name: field name from ``mapper`` (its value must be a
                           :class:`Field` object
        :return: None
        """

        def _des_to_orig(field, orig_accessor, dest_accessor):
            if isinstance(field, ModelMapper):
                field.destination_to_origin()
                return

            orig_access = field.origin_access
            dest_access = field.destination_access
            try:
                dest_field_value = dest_accessor[dest_access]
            except exc.ModelAccessorAttributeError:
                pass
            else:
                orig_accessor[orig_access] = dest_field_value

        orig_accessor = self._origin_accessor
        dest_accessor = self._destination_accessor

        if field_name:
            _des_to_orig(self._mapper_accessor[field_name], orig_accessor, dest_accessor)
            return

        for _, child in self._children:
            child.destination_to_origin()

        for _, field in self._fields:
            _des_to_orig(field, orig_accessor, dest_accessor)


    def origin_to_destination(self, field_name=None):
        """Update all the values, or some specific value from a field, from
        origin model to destination one

        :param field_name: field name from ``mapper`` (its value must be a
                           :class:`Field` object
        :return: None
        """

        def _orig_to_dest(field, orig_accessor, dest_accessor):
            if isinstance(field, ModelMapper):
                field.origin_to_destination()
                return

            orig_access = field.origin_access
            dest_access = field.destination_access
            try:
                orig_field_value = orig_accessor[orig_access]
            except exc.ModelAccessorAttributeError:
                pass
            else:
                dest_accessor[dest_access] = orig_field_value

        orig_accessor = self._origin_accessor
        dest_accessor = self._destination_accessor

        if field_name:
            _orig_to_dest(self._mapper_accessor[field_name], orig_accessor, dest_accessor)
            return

        for _, child in self._children:
            child.origin_to_destination()

        for _, field in self._fields:
            _orig_to_dest(field, orig_accessor, dest_accessor)

    def to_dict(self, only_origin=False, only_destination=False):
        dest_accessor = self._destination_accessor
        orig_accessor = self._origin_accessor
        ret = {}

        for field_name, field in self._mapper_accessor:
            if isinstance(field, ModelMapper):
                ret[field_name] = field.to_dict(only_origin=only_origin, only_destination=only_destination)
                continue
            orig_access = field.origin_access
            dest_access = field.destination_access
            if only_origin:
                ret[field_name] = orig_accessor[orig_access]
            elif only_destination:
                ret[field_name] = dest_accessor[dest_access]
            else:
                ret[field_name] = (orig_accessor[orig_access], dest_accessor[dest_access])
        return ret

    def _filter_fields_by_access(self, access, field_source):

        def compare_access(decl):
            orig_or_dest = getattr(decl[1], field_source)  # (field_name, Field)
            orig_or_dest_access = orig_or_dest.access if isinstance(orig_or_dest, FieldAccessor) else orig_or_dest
            return access == orig_or_dest_access

        return compat.filter(compare_access, self._fields)

    def filter_fields_by_orig_access(self, access):
        return self._filter_fields_by_access(access, 'origin_access')

    def filter_fields_by_dest_access(self, access):
        return self._filter_fields_by_access(access, 'destination_access')

    def filter_children_by_orig_access(self, access):
        return compat.filter(lambda decl: access == decl[1].origin_access,  # (field_name, ModelMapper)
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
    __slots__ = ('_orig_data', '_index')

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

    def origin_to_destination(self, field_name=None):
        if not self._orig_data:
            return
        super(UniformListModelMapper, self).origin_to_destination(field_name=field_name)

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

        for field_name, field in self._mapper_accessor:
            for index, _ in enumerate(model):
                update_index(index)
                if isinstance(field, ModelMapper):
                    ret[index][field_name] = field.to_dict(only_origin=True)
                else:
                    ret[index][field_name] = self._origin_accessor[field.origin_access]
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
#         for _, field in self._mapper_accessor:
#             for index, _ in enumerate(accessor_to_get.model):
#                 if isinstance(field, ModelMapper):
#                     orig_to_dest_or_vice_versa = getattr(field, func_name)
#                     orig_to_dest_or_vice_versa()
#                 else:
#                     item_to_set = link(index, field[setter_index])
#                     item_to_get = link(index, field[getter_index])
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
#         for field_name, field in self._mapper_accessor:
#             for index, _ in enumerate(model):
#                 if isinstance(field, ModelMapper):
#                     ret[index][field_name] = field.to_dict(only_destination=True)
#                 else:
#                     ret[index][field_name] = dest_accessor[link(index, field.destination_access)]
#         return ret
#
#     def _to_dict_only_origin(self):
#         orig_accessor = self._origin_accessor
#         model = self._origin_model
#         ret = [dict() for _ in range(len(model))]
#         link = ListModelMapper.LINK.format
#
#         for field_name, field in self._mapper_accessor:
#             for index, _ in enumerate(model):
#                 if isinstance(field, ModelMapper):
#                     ret[index][field_name] = field.to_dict(only_origin=True)
#                 else:
#                     ret[index][field_name] = orig_accessor[link(index, field.origin_access)]
#         return ret
