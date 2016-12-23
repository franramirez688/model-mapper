import re
from abc import ABCMeta

import six

from modelmapper import exceptions
from modelmapper.compat import filter


def handle_exceptions(get_or_set):
    def handle(*args, **kwargs):
        root = args[1]
        attr = args[2]
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

    @property
    def model(self):
        return self._model

    @staticmethod
    def split(name, pattern=None, **kwargs):
        pattern = re.compile(pattern) if pattern else ModelAccessor.SPLIT_ACCESSOR_REGEX
        return list(filter(None, pattern.split(name, **kwargs)))  # delete empty strings

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
            return root_obj[int(attr)]
        else:
            return getattr(root_obj, attr)

    @handle_exceptions
    def _set_item(self, root_obj, attr, value):
        if isinstance(root_obj, dict):
            root_obj[attr] = value
        elif isinstance(root_obj, list):
            root_obj[int(attr)] = value
        else:
            setattr(root_obj, attr, value)

    def _get_target_item(self, items):
        target_item = self._model
        getter = self._get_item
        for item in items:
            target_item = getter(target_item, item)
        return target_item

    def _get_item_value(self, item):
        split_item = item if isinstance(item, list) else self.split(item)
        return self._get_target_item(split_item) if len(split_item) > 1 else self._get_item(self._model, split_item[0])

    def _get_root_obj_and_attr(self, item):
        split_item = item if isinstance(item, list) else self.split(item)
        root_obj = self._get_target_item(split_item[:-1]) if len(split_item) > 1 else self._model
        return root_obj, split_item[-1]

    def __getitem__(self, item):
        if isinstance(item, FieldAccessor):
            return item.get_value()
        elif self.SPECIAL_LIST_INDICATOR in item:
            return SpecialListAccessor.get_item(self, item)
        else:
            return self._get_item_value(item)

    def __setitem__(self, item, value):
        if isinstance(item, FieldAccessor):
            item.set_value(value)
        elif self.SPECIAL_LIST_INDICATOR in item:
            SpecialListAccessor.set_item(self, item, value)
        else:
            root_obj, attr = self._get_root_obj_and_attr(item)
            self._set_item(root_obj, attr, value)

    def __contains__(self, item):
        try:
            self.__getitem__(item)
        except exceptions.ModelAccessorError:
            return False
        else:
            return True


class SpecialListAccessor(object):

    SPLIT_ACCESSOR_REGEX = re.compile(r"\[\*\]\.|\[\*\]")

    @staticmethod
    def split_list_items(item):
        special_list_item = ModelAccessor.split(item, pattern=SpecialListAccessor.SPLIT_ACCESSOR_REGEX, maxsplit=1)
        return special_list_item[0], special_list_item[1] if len(special_list_item) > 1 else None

    @staticmethod
    def get_item(model_accessor, item):
        list_access, list_new_items = SpecialListAccessor.split_list_items(item)
        if list_new_items is None:
            return model_accessor[list_access]
        else:
            ret = []
            for item in model_accessor[list_access]:
                item_accessor = ModelAccessor(item)
                ret.append(item_accessor[list_new_items])
            return ret

    @staticmethod
    def set_item(model_accessor, item, value):
        list_access, list_new_items = SpecialListAccessor.split_list_items(item)
        if list_new_items is None:
            model_accessor[list_access] = value
        else:
            for item in model_accessor[list_access]:
                item_accessor = ModelAccessor(item)
                item_accessor[list_new_items] = value


class ModelDictAccessor(ModelAccessor):

    def iteritems(self):
        return six.iteritems(self._model)


class FieldAccessor(object):

    __metaclass__ = ABCMeta

    def __init__(self, access):
        self.access = access
        self._parent_accessor = None

    @property
    def field(self):
        try:
            return self._parent_accessor[self.access]
        except Exception as e:
            raise exceptions.FieldAccessorError(str(e))

    @property
    def parent_accessor(self):
        return self._parent_accessor

    @parent_accessor.setter
    def parent_accessor(self, accessor):
        if isinstance(accessor, ModelAccessor):
            self._parent_accessor = accessor
            return
        raise exceptions.FieldAccessorError("{} type must be ModelAccessor".format(accessor))

    def set_value(self, value):
        raise NotImplemented

    def get_value(self):
        raise NotImplemented
