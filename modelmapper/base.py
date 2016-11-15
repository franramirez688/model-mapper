import six

from modelmapper.exceptions import ModelMapperError
from modelmapper.utils import FieldAccessor


class ModelMapper(object):
    """Linker class between an origin model and a destination one
    """
    def __init__(self, mapper, model_origin, model_destination):
        self._mapper = mapper
        self._model_origin_accessor = FieldAccessor(model_origin)
        self._model_destination_accessor = FieldAccessor(model_destination)

    @property
    def mapper(self):
        return self._mapper

    @property
    def model_origin(self):
        return self._model_origin_accessor.model

    @property
    def model_destination(self):
        return self._model_destination_accessor.model

    # def to_dict(self):
    #     origin = self._model_origin_accessor
    #     destination = self._model_destination_accessor
    #     for field_name, field in six.iteritems(self._mapper):
    #         origin[field.model_origin_access] = destination[field.model_destination_access]
    #         field.origin_to_destination()
    #         # field.get_value()
    #     return self._model_origin_accessor
    #
    # def from_dict(self, data):
    #     data_accessor = FieldAccessor(data)
    #
    #     for field_name, field in six.iteritems(self._mapper):
    #         if field.model_origin_access in data_accessor and field.setter is not None:
    #             field.set_value(data_accessor[field.model_origin_access])

    def update_list_index(self, field_name, index=0):
        try:
            orig_field, dest_field = self._mapper[field_name]
            if isinstance(orig_field, UniformListField):
                dest_field.set_value(orig_field[index])
        except KeyError:
            raise ModelMapperError("The field name {} does not exist".format(field_name))

    def update_origin(self):
        dest_accessor = self._model_destination_accessor
        for field_name, (orig_field, dest_field) in six.iteritems(self._mapper):
            orig_field.set_value(dest_accessor[dest_field.path])

    def update_destination(self):
        orig_accessor = self._model_origin_accessor
        for field_name, (orig_field, dest_field) in six.iteritems(self._mapper):
            dest_field.set_value(orig_accessor[orig_field.path])
