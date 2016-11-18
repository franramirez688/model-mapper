from collections import MutableMapping

import six

from modelmapper.exceptions import ModelMapperError
from modelmapper.utils import ModelAccessor, ModelDictAccessor


class ModelMapper(object):
    """Linker class between an origin model and a destination one
    """
    def __init__(self, origin_model, destination_model, mapper):
        assert isinstance(mapper, MutableMapping), "Mapper must be a mutable mapping (dict, OrderedDict, etc)"

        self._mapper = ModelDictAccessor(mapper)
        self._origin_model_accessor = ModelAccessor(origin_model)
        self._destination_model_accessor = ModelAccessor(destination_model)

    def _check_is_list(self, orig, dest):
        list_indicator = ModelAccessor.SPECIAL_LIST_INDICATOR
        return list_indicator in orig or list_indicator in dest

    def _prepare_mapper(self):
        model_mappers = set()
        orig_accessor = self._origin_model_accessor
        dest_accessor = self._destination_model_accessor
        check_is_list = self._check_is_list

        for link_name, link_args in self._mapper.iteritems():
            if len(link_args) == 3:
                is_list = check_is_list(link_args[0], link_args[1])
                model_mapper_args = (orig_accessor[link_args[0]],
                                     dest_accessor[link_args[1]],
                                     link_args[2])
                model_mapper = UniformListModelMapper(*model_mapper_args) if is_list else ModelMapper(*model_mapper_args)
                model_mappers.add((link_name, model_mapper))
        return model_mappers

    def prepare_mapper(self):
        model_mappers = self._prepare_mapper()
        mapper = self._mapper

        for (link_name, model_mapper) in model_mappers:
            mapper[link_name] = model_mapper
            mapper[link_name].prepare_mapper()

    def update_origin(self):
        dest_accessor = self._destination_model_accessor
        for link_name, link_value in six.iteritems(self._mapper):
            if isinstance(link_value, ModelMapper):
                link_value.update_origin()
                continue
            link_value[0].set_value(dest_accessor[link_value[1].access])

    def update_destination(self):
        orig_accessor = self._origin_model_accessor
        for link_name, link_value in six.iteritems(self._mapper):
            if isinstance(link_value, ModelMapper):
                link_value.update_origin()
                continue
            link_value[1].set_value(orig_accessor[link_value[0].access])

    def __getitem__(self, item):
        return self._mapper[item]

    def __setitem__(self, key, value):
        self._mapper[key] = value


# TODO: At this moment is only possible to be the origin a list


class UniformListModelMapper(ModelMapper):

    def __init__(self, origin_model, destination_model, mapper):
        assert isinstance(origin_model, list), "Origin model must be a list with uniform data"

        self._orig_data = origin_model
        self._current_index = 0
        super(UniformListModelMapper, self).__init__(origin_model[0], destination_model, mapper)

    @property
    def current_index(self):
        return self._current_index

    @current_index.setter
    def current_index(self, index):
        try:
            self._origin_model_accessor = ModelAccessor(self._orig_data[index])
            self._current_index = index
            self.update_destination()
        except IndexError:
            raise ModelMapperError("The index {} is out of range".format(index))
