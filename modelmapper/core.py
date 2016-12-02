from collections import MutableMapping

from modelmapper.exceptions import ModelMapperError
from modelmapper.accessors import ModelAccessor, ModelDictAccessor, FieldAccessor


class Mapper(object):

    def __init__(self, origin_model, destination_model, mapper):
        assert isinstance(mapper, MutableMapping), "Mapper must be a mutable mapping (dict, OrderedDict, etc)"

        self._origin_model = origin_model
        self._destination_model = destination_model
        self._mapper = mapper

    @staticmethod
    def factory(orig_model, dest_model, mapper):
        if isinstance(orig_model, list) and isinstance(dest_model, list):
            return ListModelMapper(orig_model, dest_model, mapper)
        elif isinstance(orig_model, list) or isinstance(dest_model, list):
            return UniformListModelMapper(orig_model, dest_model, mapper)
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


class ModelMapper(Mapper):
    """Linker class between an origin model and a destination one
    """

    def __init__(self, origin_model, destination_model, mapper):
        super(ModelMapper, self).__init__(origin_model, destination_model, mapper)

        self._mapper_accessor = ModelDictAccessor(mapper)
        self._origin_model_accessor = ModelAccessor(origin_model)
        self._destination_model_accessor = ModelAccessor(destination_model)

        self._children_accesses = set()

    def set_origin_model(self, model):
        self._origin_model = model
        self._origin_model_accessor = ModelAccessor(model)

        for origin_access, _, mapper in self._children_accesses:
            mapper.set_origin_model(self._origin_model_accessor[origin_access])

    def _get_new_model_mapper(self, orig_model, dest_model, mapper):
        model_mapper = Mapper.factory(self._origin_model_accessor[orig_model],
                                      self._destination_model_accessor[dest_model],
                                      mapper)
        self._children_accesses.add((orig_model, dest_model, model_mapper))
        return model_mapper

    def set_field_parent_accessor(self, orig_field, dest_field):

        def _set_parent_accessor(field, parent_accessor):
            if isinstance(field, FieldAccessor):
                field.parent_accessor = parent_accessor

        _set_parent_accessor(orig_field, self._origin_model_accessor)
        _set_parent_accessor(dest_field, self._destination_model_accessor)

    def _prepare_mapper_and_get_new_mappers(self):
        set_field_parent_accessor = self.set_field_parent_accessor
        get_new_model_mapper = self._get_new_model_mapper

        for link_name, link_args in self._mapper_accessor.iteritems():
            if len(link_args) == 2:
                set_field_parent_accessor(*link_args)
            elif len(link_args) == 3:
                yield link_name, get_new_model_mapper(*link_args)

    def prepare_mapper(self):
        mapper = self._mapper_accessor
        new_model_mappers = self._prepare_mapper_and_get_new_mappers() or []

        for (link_name, model_mapper) in new_model_mappers:
            mapper[link_name] = model_mapper
            mapper[link_name].prepare_mapper()

    def update_origin(self):
        dest_accessor = self._destination_model_accessor
        orig_accessor = self._origin_model_accessor

        for _, link_value in self._mapper_accessor.iteritems():
            if isinstance(link_value, ModelMapper):
                link_value.update_origin()
            else:
                orig_accessor[link_value[0]] = dest_accessor[link_value[1]]

    def update_destination(self):
        dest_accessor = self._destination_model_accessor
        orig_accessor = self._origin_model_accessor

        for _, link_value in self._mapper_accessor.iteritems():
            if isinstance(link_value, ModelMapper):
                link_value.update_destination()
            else:
                dest_accessor[link_value[1]] = orig_accessor[link_value[0]]


    def __getitem__(self, item):
        return self._mapper_accessor[item]

    def __setitem__(self, key, value):
        self._mapper_accessor[key] = value

    __getattr__ = __getitem__  # If getattr(self, 'link')


class ListModelMapper(ModelMapper):

    LINK = '[{}].{}'

    def __init__(self, origin_model, destination_model, mapper):
        self._current_index = 0
        super(ListModelMapper, self).__init__(origin_model, destination_model, mapper)


    def update_origin(self):
        dest_accessor = self._destination_model_accessor
        orig_accessor = self._origin_model_accessor
        model_list_range = range(len(self.destination_model))
        link = ListModelMapper.LINK.format

        for _, link_value in self._mapper_accessor.iteritems():
            if isinstance(link_value, ModelMapper):
                link_value.update_origin()
                continue
            for index in model_list_range:
                orig_accessor[link(index, link_value[0])] = dest_accessor[link(index, link_value[1])]

    def update_destination(self):
        dest_accessor = self._destination_model_accessor
        orig_accessor = self._origin_model_accessor
        model_list_range = range(len(self.origin_model))
        link = ListModelMapper.LINK.format

        for _, link_value in self._mapper_accessor.iteritems():
            if isinstance(link_value, ModelMapper):
                link_value.update_destination()
                continue
            for index in model_list_range:
                dest_accessor[link(index, link_value[1])] = orig_accessor[link(index, link_value[0])]


# TODO: At this moment is only possible to be the origin a list


class UniformListModelMapper(ModelMapper):

    def __init__(self, origin_model, destination_model, mapper):
        assert isinstance(origin_model, list), "Origin model must be a list with uniform data"

        self._orig_data = origin_model
        self._current_index = 0
        super(UniformListModelMapper, self).__init__(origin_model[0], destination_model, mapper)

    def set_origin_model(self, model):
        self._orig_data = model
        self._origin_model = model[self._current_index]
        self._origin_model_accessor = ModelAccessor(self.origin_model)

        for mapper, origin_access, _ in self._children_accesses:
            mapper.origin_model = self._origin_model_accessor[origin_access]

    @property
    def current_index(self):
        return self._current_index

    @current_index.setter
    def current_index(self, index):
        try:
            self._current_index = index
            self._origin_model = self._orig_data[index]
            self._origin_model_accessor = ModelAccessor(self.origin_model)
            super(UniformListModelMapper, self).set_origin_model(self.origin_model)
            self.update_destination()
        except IndexError:
            raise ModelMapperError("The index {} is out of range".format(index))
