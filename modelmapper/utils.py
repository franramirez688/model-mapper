import re
from abc import ABCMeta

import six

from modelmapper import exceptions


def handle_exceptions(get_or_set):
    def handle(*args, **kwargs):
        root = args[0]
        attr = args[1]
        try:
            return get_or_set(*args, **kwargs)
        except AttributeError:
            raise exceptions.ModelAccessorAttributeError(
                "{root} has not the attribute {attr}".format(root=root, attr=attr))
        except IndexError:
            raise exceptions.ModelAccessorIndexError(
                "Not exist the index {index} in {root} object".format(index=attr, root=root))
        except KeyError:
            raise exceptions.ModelAccessorKeyError(
                "{root} has not the key {attr}".format(root=root, attr=attr))
        except Exception as e:
            raise exceptions.ModelAccessorError(str(e))
    return handle


class ModelAccessor(object):

    SPLIT_ACCESSOR_REGEX = re.compile(r"[.\[\]]+")
    SPECIAL_LIST_INDICATOR = "[*]"
    CUSTOMIZED_GETTER_METHOD = "get_value"
    CUSTOMIZED_SETTER_METHOD = "set_value"

    def __init__(self, model):
        """
        :param model: dictionary or a simple object
        """
        self._model = model
        self._visited_objects = None

    @property
    def model(self):
        return self._model

    def split(self, name, pattern=None):
        pattern = re.compile(pattern) if pattern else self.SPLIT_ACCESSOR_REGEX
        return filter(None, pattern.split(name))  # delete empty strings

    def get(self, name, default=None):
        try:
            return self.__getitem__(name)
        except exceptions.ModelAccessorError:
            return default

    @handle_exceptions
    def _get_item(self, root_obj, attr):
        if isinstance(root_obj, dict):
            return root_obj[attr]
        elif isinstance(root_obj, (list, tuple)):
            if attr == self.SPECIAL_LIST_INDICATOR[1]:
                return root_obj
            return root_obj[int(attr)]
        else:
            return getattr(root_obj, attr)

    @handle_exceptions
    def _set_item(self, root_obj, attr, value):
        if isinstance(root_obj, dict):
            root_obj[attr] = value
        elif isinstance(root_obj, list):
            if attr == self.SPECIAL_LIST_INDICATOR[1]:
                root_obj = value
            root_obj[int(attr)] = value
        else:
            setattr(root_obj, attr, value)

    def _get_target_item(self, items):
        target_item = self._model
        getter = self._get_item
        for item in items:
            target_item = getter(target_item, item)
        return target_item

    def __getitem__(self, item):
        if isinstance(item, FieldAccessor):
            if item.access_object is None:
                item.access_object = self.__getitem__(item.access_path)
            return item.get_value()
        split_item = self.split(item)
        return self._get_target_item(split_item) if len(split_item) > 1 else self._get_item(self._model, split_item[0])

    def __setitem__(self, item, value):
        if isinstance(item, FieldAccessor):
            if item.access_object is None:
                item.access_object = self.__getitem__(item.access_path)
            item.set_value(value)
            return
        split_item = self.split(item)
        parent_target_item = self._get_target_item(split_item[:-1]) if len(split_item) > 1 else self._model
        self._set_item(parent_target_item, split_item[-1], value)

    def __contains__(self, item):
        try:
            self.__getitem__(item)
        except exceptions.ModelAccessorError:
            return False
        else:
            return True


class ModelContainer(object):

        def __init__(self):
            self._cached_objects = None


class ModelDictAccessor(ModelAccessor):

    def iteritems(self):
        return six.iteritems(self._model)


class FieldAccessor(object):

    __metaclass__ = ABCMeta

    def __init__(self, access_path):
        self.access_path = access_path
        self.access_object = None

    def set_value(self, value):
        raise NotImplemented

    def get_value(self):
        raise NotImplemented


# class FieldListAccessor(ModelAccessor):
#
#     @handle_exceptions
#     def _get_item(self, root_obj, attr):
#         return root_obj[attr]
#
#     @handle_exceptions
#     def _set_item(self, root_obj, attr, value):
#         root_obj[int(attr)] = value
#
#
# class FieldTupleAccessor(FieldListAccessor):
#
#     @handle_exceptions
#     def _set_item(self, root_obj, attr, value):
#         raise exceptions.ModelAccessorAssignmentError("'tuple' object does not support item assignment")
