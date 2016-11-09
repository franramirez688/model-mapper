import six
import addict

from modelmapper.utils import ModelDataAccessor


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
        self._model_data = ModelDataAccessor(model_data)
        self._root_class = root_class


    def _map_and_link(self):
        for field_name, field in six.iteritems(self._mapper):
            field.object_pointed = object_path_resolver(self._root_class, field.object_path)
            field.set_value(self._model_data[field.model_data_path])

    def to_dict(self):
        for field_name, field in six.iteritems(self._mapper):
            self._model_data[field.model_data_path] = field.get_value()
        return self._model_data


    def from_dict(self, data):
        model_data = ModelDataAccessor(data)

        for field_name, field in six.iteritems(self._mapper):
            if field.model_data_path in model_data and field.setter is not None:
                field.set_value(model_data[field.model_data_path])

#
# import six
#
# from .exceptions import FormError
# from .fields import Field
#
#
# class _MetaModelForm(type):
#
#     def __new__(cls, name, bases, attrs):
#         cls = type.__new__(cls, name, bases, attrs)
#         cls._widgets_instances = {}
#         cls.__set_widgets_instances(attrs)
#         cls.__update_widgets_instances_from_parents(bases)
#         return cls
#
#     def __set_widgets_instances(cls, attrs):
#         for attr_name, attr_value in six.iteritems(attrs):
#             if isinstance(attr_value, Field):
#                 cls._widgets_instances[attr_name] = attr_value
#
#
#     def __update_widgets_instances_from_parents(cls, bases):
#         for base in bases:
#             if hasattr(base, '_widgets_instances'):
#                 cls._widgets_instances.update(base._widgets_instances)
#
#
# class ModelLink(object):
#
#     __metaclass__ = _MetaModelForm
#
#     def __init__(self, ui):
#         self._ui = ui
#         self._init_objects_instances()
#
#     @property
#     def ui(self):
#         return self._ui
#
#     def _init_objects_instances(self):
#         for attr_name, attr_value in six.iteritems(self._widgets_instances):
#             source_object_name = attr_value.source or attr_name
#             if hasattr(self._ui, source_object_name ):
#                 attr_value.object_pointed = getattr(self._ui, source_object_name)
#
#     @property
#     def fields(self):
#         for field in six.itervalues(self._widgets_instances):
#             yield field
#
#     def walker(self):
#         for name, field in six.iteritems(self._widgets_instances):
#             if field.getter is not None:
#                 yield name, field.get_value()
#
#     def to_dict(self):
#         return dict(self.walker())
#
#     def from_dict(self, data):
#         """Update all the objects values from a data dictionary passed
#
#         :type data: dict
#         """
#         assert isinstance(data, dict), "Data must be a dictionary"
#
#         for name, field in six.iteritems(self._widgets_instances):
#             if name in data and field.setter is not None:
#                 field.set_value(data[name])
#
#
# class SubForm(object):
#
#     def __init__(self, modelform):
#         self._modelform_type = modelform
#         self._modelform_instance = None
#         self._name = None
#
#     def instantiate_subform(self, ui, name):
#         self._name = name
#         self._modelform_instance = self._modelform_type(ui)
#
#     def to_dict(self):
#         return self._modelform_instance.to_dict()
#
#     def from_dict(self, data):
#         self._modelform_instance.from_dict(data)
#
#
# class ListSubForm(SubForm):
#
#     def __init__(self, modelform):
#         super(ListSubForm, self).__init__(modelform)
#         self._data = None
#
#     def from_object(self, data):
#         self._data = data[self._name]
#
#     def from_dict(self, data):
#         self.from_object(data)
#
#     def to_object(self, data=None):
#         self._form_instance.model_.commit()
#         return {self._name: self._data}
#
#     def to_dict(self, data=None):
#         return self.to_object(data)
#
#
# class _MetaForm(type):
#
#     def __new__(cls, name, bases, attrs):
#         cls = type.__new__(cls, name, bases, attrs)
#         cls._subforms = {}
#         for name, value in six.iteritems(attrs):
#             if isinstance(value, SubForm):
#                 cls._subforms[name] = value
#
#         return cls
#
#
# class Form(object):
#
#     __metaclass__ = _MetaForm
#
#     def __init__(self, ui):
#         for name, subform in self._subforms.items():
#             subform.instantiate_subform(self._get_ui_from_name(ui, name), name)
#
#     def from_object(self, object_):
#         for form in self._all():
#             form.from_object(object_)
#
#     def to_object(self, object_):
#         for form in self._all():
#             form.to_object(object_)
#
#     def from_dict(self, object_):
#         for name, form in six.iteritems(self._subforms):
#             form.from_dict(object_)
#
#     def to_dict(self):
#         res = {}
#         for name, subform in six.iteritems(self._subforms):
#             res.update(subform.to_dict())
#         return res
#
#     def _all(self):
#         for subform in six.itervalues(self._subforms):
#             yield subform
#
#     def _get_ui_from_name(self, ui, name):
#         try:
#             return getattr(ui, name)
#         except AttributeError:
#             raise FormError('Does not exist the Form: "{}" defined in'
#                             ' the parent Form: "{}"'.format(name, self.__class__.__name__))
