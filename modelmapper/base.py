import six

from modelmapper.exceptions import ModelMapperError
from modelmapper.utils import FieldAccessor


class ModelMapper(object):
    """Linker class between an origin model and a destination one
    """
    def __init__(self, model_origin, model_destination, mapper):
        self._mapper = mapper
        self._model_origin_accessor = FieldAccessor(model_origin)
        self._model_destination_accessor = FieldAccessor(model_destination)

    # @staticmethod
    # def factory(type_):
    #     if type_ == "uniform-list":
    #         return UniformListModelMapper
    #     return ModelMapper

    def _check_is_list(self, orig, dest):
        list_indicator = FieldAccessor.SPECIAL_LIST_INDICATOR
        return list_indicator in orig or list_indicator in dest

    def walker_mapper(self):
        model_mappers = set()
        orig_accessor = self._model_origin_accessor
        dest_accessor = self._model_destination_accessor
        mapper = self._mapper
        check_is_list = self._check_is_list

        for link_name, link_args in six.iteritems(mapper):
            if len(link_args) == 3:
                is_list = check_is_list(link_args[0], link_args[1])
                model_mapper_args = [orig_accessor[link_args[0]],
                                     dest_accessor[link_args[1]],
                                     link_args[3]]
                model_mappers.add((link_name, model_mapper_args, is_list))

        for (link_name, model_mapper_args, is_list) in model_mappers:
            mapper[link_name] = UniformListModelMapper(*model_mapper_args) if is_list else ModelMapper(*model_mapper_args)
            mapper[link_name].walker_mapper()

    def update_origin(self):
        dest_accessor = self._model_destination_accessor
        for link_name, (orig_field, dest_field) in six.iteritems(self._mapper):
            orig_field.set_value(dest_accessor[dest_field.path])

    def update_destination(self):
        orig_accessor = self._model_origin_accessor
        for link_name, (orig_field, dest_field) in six.iteritems(self._mapper):
            dest_field.set_value(orig_accessor[orig_field.path])


class UniformListModelMapper(ModelMapper):

    def __init__(self, *args, **kwargs):
        super(UniformListModelMapper, self).__init__(*args, **kwargs)
        self._current_index = 0

    def update_list_index(self, link_name, index=0):
        try:
            orig_field, dest_field = self._mapper[link_name]
            dest_field.set_value(orig_field[index])
        except KeyError:
            raise ModelMapperError("The field name {} does not exist".format(link_name))
