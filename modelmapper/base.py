from collections import MutableMapping

import six

from modelmapper.exceptions import ModelMapperError
from modelmapper.utils import ModelAccessor, ModelDictAccessor


class ModelMapper(object):
    """Linker class between an origin model and a destination one
    """

    def __init__(self, origin_model, destination_model, mapper):
        assert isinstance(mapper, MutableMapping), "Mapper must be a mutable mapping (dict, OrderedDict, etc)"

        self._origin_model = origin_model
        self._destination_model = destination_model
        self._mapper = mapper

        self._mapper_accessor = ModelDictAccessor(mapper)
        self._origin_model_accessor = ModelAccessor(origin_model)
        self._destination_model_accessor = ModelAccessor(destination_model)

        self._children_accesses = set()

    @property
    def origin_model(self):
        return self._origin_model

    def set_origin_model(self, model):
        self._origin_model = model
        self._origin_model_accessor = ModelAccessor(model)

        for mapper, origin_access, _ in self._children_accesses:
            mapper.set_origin_model(self._origin_model_accessor[origin_access])

    def _check_is_list(self, orig, dest):
        list_indicator = ModelAccessor.SPECIAL_LIST_INDICATOR
        return list_indicator in orig or list_indicator in dest

    def _prepare_mapper(self):
        orig_accessor = self._origin_model_accessor
        dest_accessor = self._destination_model_accessor
        check_is_list = self._check_is_list
        children_accesses = self._children_accesses

        for link_name, link_args in self._mapper_accessor.iteritems():
            if len(link_args) == 3:
                is_list = check_is_list(link_args[0], link_args[1])
                model_mapper_args = (orig_accessor[link_args[0]],
                                     dest_accessor[link_args[1]],
                                     link_args[2])
                model_mapper = UniformListModelMapper if is_list else ModelMapper
                model_mapper = model_mapper(*model_mapper_args)
                children_accesses.add((model_mapper, link_args[0], link_args[1]))

                yield link_name, model_mapper

    def prepare_mapper(self):
        model_mappers = self._prepare_mapper()
        if model_mappers is None:
            return

        mapper = self._mapper_accessor
        for (link_name, model_mapper) in model_mappers:
            mapper[link_name] = model_mapper
            mapper[link_name].prepare_mapper()

    def _update(self, origin=False):
        dest_accessor = self._destination_model_accessor
        orig_accessor = self._origin_model_accessor
        for _, link_value in six.iteritems(self._mapper_accessor):
            if isinstance(link_value, ModelMapper):
                if origin:
                    link_value.update_origin()
                else:
                    link_value.update_destination()
                continue
            if origin:
                orig_accessor[link_value[0]] = dest_accessor[link_value[1]]
            else:
                dest_accessor[link_value[1]] = orig_accessor[link_value[0]]

    def update_origin(self):
        self._update(origin=True)

    def update_destination(self):
        self._update()

    def __getitem__(self, item):
        return self._mapper_accessor[item]

    def __setitem__(self, key, value):
        self._mapper_accessor[key] = value

    __getattr__ = __getitem__  # If getattr(self, 'link')


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
        self._origin_model_accessor = ModelAccessor(self._origin_model)

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
            self._origin_model_accessor = ModelAccessor(self._origin_model)
            super(UniformListModelMapper, self).set_origin_model(self._origin_model)
            self.update_destination()
        except IndexError:
            raise ModelMapperError("The index {} is out of range".format(index))
