import six

from modelmapper.utils import ModelAccessor


def object_path_resolver(root_class, path_to_object):
    list_attrs = path_to_object.split('.')
    root_object = root_class
    for attr_ in list_attrs:
        try:
            root_object = getattr(root_object, attr_)
        except AttributeError:
            raise Exception("The path %s to get the original object does not exist" % path_to_object)
    return root_object


class ModelMapper(object):
    """Linker class between model data and root class instance
    """
    def __init__(self, mapper, model_data, root_class):
        """
        :param mapper: dict with linking rules
        :param model_data: dict with all the model data
        :param root_class: object instance to get links with its model data
        """
        self._mapper = mapper
        self._model_data = ModelAccessor(model_data)
        self._root_class = ModelAccessor(root_class)

    def _map_and_link(self):
        for field_name, field in six.iteritems(self._mapper):
            field.object_pointed = object_path_resolver(self._root_class, field.object_path)
            field.set_value(self._model_data[field.model_data_path])

    def to_dict(self):
        for field_name, field in six.iteritems(self._mapper):
            self._model_data[field.model_data_path] = field.get_value()
        return self._model_data

    def from_dict(self, data):
        model_data = ModelAccessor(data)

        for field_name, field in six.iteritems(self._mapper):
            if field.model_data_path in model_data and field.setter is not None:
                field.set_value(model_data[field.model_data_path])
