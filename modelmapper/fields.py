import inspect

from modelmapper.exceptions import FieldError


class Field(object):

    def __init__(self, access, getter=None, setter=None):
        self.setter = setter
        self.getter = getter
        self.access = access
        self.object_destination_instance = None

    def set_value(self, value):
        if self.setter is None:
            return
        elif self.object_destination_instance is None:
            raise FieldError("The object instance can not be None")

        try:
            setter = getattr(self.object_destination_instance, self.setter)
            if inspect.ismethod(setter):
                setter(value)
            setattr(self.object_destination_instance, self.setter, value)
        except AttributeError:
            FieldError("The class {class_name} does not have {attr_name} attribute".format(
                class_name=self.object_destination_instance.__class__.__name__,
                attr_name=self.setter))

    def get_value(self):
        if self.getter is None:
            return
        elif self.object_destination_instance is None:
            raise FieldError("The object instance can not be None")

        try:
            getter = getattr(self.object_destination_instance, self.getter)
            if inspect.ismethod(getter):
                return getter()
            return getter
        except AttributeError:
            FieldError("The class {class_name} does not have {attr_name} attribute".format(
                class_name=self.object_destination_instance.__class__.__name__,
                attr_name=self.getter))
