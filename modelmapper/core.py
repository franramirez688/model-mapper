from collections import MutableMapping
from copy import deepcopy

from modelmapper.exceptions import ModelMapperError
from modelmapper.accessors import ModelAccessor, ModelDictAccessor, FieldAccessor


class _Mapper(object):

    def __init__(self, origin_model, destination_model, mapper):
        assert isinstance(mapper, MutableMapping), "Mapper must be a mutable mapping (dict, OrderedDict, etc)"

        self._origin_model = origin_model
        self._destination_model = destination_model
        self._mapper = mapper

        self._mapper_accessor = ModelDictAccessor(mapper)
        self._origin_accessor = ModelAccessor(origin_model)
        self._destination_accessor = ModelAccessor(destination_model)

    @staticmethod
    def factory(orig_model, dest_model, mapper, *args):
        if isinstance(orig_model, list) and isinstance(dest_model, list):
            return ListModelMapper(orig_model, dest_model, mapper, *args)
        elif isinstance(orig_model, list) or isinstance(dest_model, list):
            return UniformListModelMapper(orig_model, dest_model, mapper, *args)
        else:
            return ModelMapper(orig_model, dest_model, mapper)

    @property
    def origin_model(self):
        return self._origin_model

    @property
    def destination_model(self):
        return self._destination_model

    @property
    def mapper(self):
        return self._mapper

    @property
    def origin_accessor(self):
        return self._origin_accessor

    @property
    def destination_accessor(self):
        return self._destination_accessor

    @property
    def mapper_accessor(self):
        return self._mapper_accessor


class ModelMapper(_Mapper):
    """Linker class between an origin model and a destination one
    """

    def __init__(self, origin_model, destination_model, mapper):
        super(ModelMapper, self).__init__(origin_model, destination_model, mapper)

        self._children_accesses = set()

    def set_origin_model(self, model):
        self._origin_model = model
        self._origin_accessor = ModelAccessor(model)

        for origin_access, _, mapper in self._children_accesses:
            mapper.set_origin_model(self._origin_accessor[origin_access])

    def _get_new_model_mapper(self, *args):
        orig_access, dest_access = args[0], args[1]
        model_mapper = _Mapper.factory(self._origin_accessor[orig_access],
                                       self._destination_accessor[dest_access],
                                       *args[2:])
        child = (orig_access, dest_access, model_mapper)

        self._children_accesses.add(child)
        return model_mapper

    def set_field_parent_accessor(self, orig_field, dest_field):

        def _set_parent_accessor(field, parent_accessor):
            if isinstance(field, FieldAccessor):
                field.parent_accessor = parent_accessor

        _set_parent_accessor(orig_field, self._origin_accessor)
        _set_parent_accessor(dest_field, self._destination_accessor)

    def _prepare_mapper_and_get_new_mappers(self):
        set_field_parent_accessor = self.set_field_parent_accessor
        get_new_model_mapper = self._get_new_model_mapper

        for link_name, link_args in self._mapper_accessor.iteritems():
            args_length = len(link_args)
            if args_length == 2:
                set_field_parent_accessor(*link_args)
            elif args_length >= 3:
                yield link_name, get_new_model_mapper(*link_args)

    def prepare_mapper(self):
        mapper = self._mapper_accessor
        new_model_mappers = self._prepare_mapper_and_get_new_mappers() or []

        for (link_name, model_mapper) in new_model_mappers:
            mapper[link_name] = model_mapper
            mapper[link_name].prepare_mapper()

    def destination_to_origin(self):
        dest_accessor = self._destination_accessor
        orig_accessor = self._origin_accessor

        for _, link_value in self._mapper_accessor.iteritems():
            if isinstance(link_value, ModelMapper):
                link_value.destination_to_origin()
            else:
                orig_accessor[link_value[0]] = dest_accessor[link_value[1]]

    def origin_to_destination(self):
        dest_accessor = self._destination_accessor
        orig_accessor = self._origin_accessor

        for _, link_value in self._mapper_accessor.iteritems():
            if isinstance(link_value, ModelMapper):
                link_value.origin_to_destination()
            else:
                dest_accessor[link_value[1]] = orig_accessor[link_value[0]]

    def __getitem__(self, item):
        return self._mapper_accessor[item]

    def __setitem__(self, key, value):
        self._mapper_accessor[key] = value

    __getattr__ = __getitem__  # If getattr(self, 'link')


class ListModelMapper(ModelMapper):

    LINK = '[{}].{}'

    def __init__(self, origin_model, destination_model, mapper, autoresize=True):
        self.autoresize = autoresize
        super(ListModelMapper, self).__init__(origin_model, destination_model, mapper)

    def destination_to_origin(self):
        dest_accessor = self._destination_accessor
        orig_accessor = self._origin_accessor
        model = self.destination_model
        link = ListModelMapper.LINK.format

        while self.autoresize and len(orig_accessor.model) < len(dest_accessor.model):
            orig_accessor.model.append(deepcopy(orig_accessor.model[-1]))

        for _, link_value in self._mapper_accessor.iteritems():
            if isinstance(link_value, ModelMapper):
                link_value.destination_to_origin()
            else:
                for index, _ in enumerate(model):
                    orig_accessor[link(index, link_value[0])] = dest_accessor[link(index, link_value[1])]

    def origin_to_destination(self):
        dest_accessor = self._destination_accessor
        orig_accessor = self._origin_accessor
        model = self.origin_model
        link = ListModelMapper.LINK.format

        while self.autoresize and len(orig_accessor.model) > len(dest_accessor.model):
            dest_accessor.model.append(deepcopy(dest_accessor.model[-1]))

        for _, link_value in self._mapper_accessor.iteritems():
            if isinstance(link_value, ModelMapper):
                link_value.origin_to_destination()
            else:
                for index, _ in enumerate(model):
                    dest_accessor[link(index, link_value[1])] = orig_accessor[link(index, link_value[0])]


# TODO: At this moment is only possible to be the origin a list


class UniformListModelMapper(ModelMapper):

    def __init__(self, origin_model, destination_model, mapper, index=0):
        assert isinstance(origin_model, list), "Origin model must be a list with uniform data"

        self._orig_data = origin_model
        self._index = index
        super(UniformListModelMapper, self).__init__(origin_model[index], destination_model, mapper)

    def set_origin_model(self, model):
        self._orig_data = model
        self._origin_model = model[self._index]
        self._origin_accessor = ModelAccessor(self.origin_model)

        for mapper, origin_access, _ in self._children_accesses:
            mapper.origin_model = self._origin_accessor[origin_access]

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        try:
            self._index = index
            self._origin_model = self._orig_data[index]
            self._origin_accessor = ModelAccessor(self.origin_model)
            super(UniformListModelMapper, self).set_origin_model(self.origin_model)
            self.origin_to_destination()
        except IndexError:
            raise ModelMapperError("The index {} is out of range".format(index))
