import six

from modelmapper.utils import ModelAccessor


class ModelMapper(object):
    """Linker class between an origin model and destination model
    """
    def __init__(self, mapper, model_origin, model_destination):
        self._mapper = mapper
        self._model_origin_accessor = ModelAccessor(model_origin)
        self._model_destination_accessor = ModelAccessor(model_destination)

    @property
    def mapper(self):
        return self._mapper

    @property
    def model_origin(self):
        return self._model_origin_accessor.model

    @property
    def model_destination(self):
        return self._model_destination_accessor.model

    def _map_and_link(self):
        for field_name, field in six.iteritems(self._mapper):
            field.object_destination_instance = self._model_destination_accessor[field.object_access]
            field.set_value(self._model_origin_accessor[field.model_origin_access])

    def to_dict(self):
        origin = self._model_origin_accessor
        destination = self._model_destination_accessor
        for field_name, field in six.iteritems(self._mapper):
            origin[field.model_origin_access] = destination[field.model_destination_access]
            field.origin_to_destination()
            # field.get_value()
        return self._model_origin_accessor

    def from_dict(self, data):
        data_accessor = ModelAccessor(data)

        for field_name, field in six.iteritems(self._mapper):
            if field.model_origin_access in data_accessor and field.setter is not None:
                field.set_value(data_accessor[field.model_origin_access])
