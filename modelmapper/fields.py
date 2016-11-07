

import inspect

from modelmapper.exceptions import FieldError


class Field(object):

    def __init__(self, model_data_path, object_path, getter=None, setter=None):
        self.setter = setter
        self.getter = getter
        self.model_data_path = model_data_path
        self.object_path = object_path
        self.object_pointed = None

    def set_value(self, value):
        if self.setter is None:
            return
        elif self.object_pointed is None:
            raise FieldError("The object instance can not be None")

        try:
            setter = getattr(self.object_pointed, self.setter)
            if inspect.ismethod(setter):
                setter(value)
            setattr(self.object_pointed, self.setter, value)
        except AttributeError:
            FieldError("The class {class_name} does not have {attr_name} attribute".format(
                class_name=self.object_pointed.__class__.__name__,
                attr_name=self.setter))

    def get_value(self):
        if self.getter is None:
            return
        elif self.object_pointed is None:
            raise FieldError("The object instance can not be None")

        try:
            getter = getattr(self.object_pointed, self.getter)
            if inspect.ismethod(getter):
                return getter()
            return getter
        except AttributeError:
            FieldError("The class {class_name} does not have {attr_name} attribute".format(
                class_name=self.object_pointed.__class__.__name__,
                attr_name=self.getter))
