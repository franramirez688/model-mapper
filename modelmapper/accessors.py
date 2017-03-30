import re
from abc import ABCMeta, abstractmethod

from modelmapper import exceptions as exc
import modelmapper.compat as compat

def handle_exceptions(f):

    def handle(*args, **kwargs):
        root = args[1]
        attr = args[2]
        try:
            return f(*args, **kwargs)
        except AttributeError:
            raise exc.ModelAccessorAttributeError(
                "{root} has not the attribute {attr}".format(root=root, attr=attr))
        except IndexError:
            raise exc.ModelAccessorIndexError(
                "Not exist the index {index} in {root} object".format(index=attr, root=root))
        except KeyError:
            raise exc.ModelAccessorKeyError(
                "{root} has not the key {attr}".format(root=root, attr=attr))
        except Exception as e:
            raise exc.ModelAccessorError(str(e))
    return handle


class ModelAccessor(object):
    __slots__ = ('_model',)

    SPLIT_ACCESSOR_REGEX = re.compile(r"[.\[\]]+")
    SPECIAL_LIST_INDICATOR = "[*]"
    CUSTOMIZED_GETTER_METHOD = "get_value"
    CUSTOMIZED_SETTER_METHOD = "set_value"

    def __init__(self, model):
        """
        :param model: dictionary or a simple object
        """
        self._model = model

    def __iter__(self):
        if isinstance(self._model, dict):
            return compat.iteritems(self._model)
        else:
            try:
                return iter(self._model)
            except TypeError:
                raise exc.ModelAccessorError("Model {} object is not iterable")

    def __getitem__(self, item):
        if isinstance(item, FieldAccessor):
            if item.parent_accessor is None:
                item.parent_accessor = self
            return item.get_value()
        elif self.SPECIAL_LIST_INDICATOR in item:
            return SpecialListAccessor.get_item(self, item)
        else:
            return self._get_item_value(item)

    def __setitem__(self, item, value):
        if isinstance(item, FieldAccessor):
            if item.parent_accessor is None:
                item.parent_accessor = self
            item.set_value(value)
        elif self.SPECIAL_LIST_INDICATOR in item:
            SpecialListAccessor.set_item(self, item, value)
        else:
            root_obj, attr = self._get_root_obj_and_attr(item)
            self._set_item(root_obj, attr, value)

    def __contains__(self, item):
        try:
            self.__getitem__(item)
        except exc.ModelAccessorError:
            return False
        else:
            return True

    @property
    def model(self):
        return self._model

    @staticmethod
    def split(name, pattern=None, **kwargs):
        pattern = re.compile(pattern) if pattern else ModelAccessor.SPLIT_ACCESSOR_REGEX
        return compat.filter(None, pattern.split(name, **kwargs))  # delete empty strings

    def get(self, name, default=None):
        try:
            return self.__getitem__(name)
        except exc.ModelAccessorError:
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
        split_item = item if isinstance(item, list) else list(ModelAccessor.split(item))
        return self._get_target_item(split_item)

    def _get_root_obj_and_attr(self, item):
        split_item = item if isinstance(item, list) else list(ModelAccessor.split(item))
        root_obj = self._get_target_item(split_item[:-1]) if len(split_item) > 1 else self._model
        return root_obj, split_item[-1]


class SpecialListAccessor(object):

    SPLIT_ACCESSOR_REGEX = re.compile(r"\[\*\]\.|\[\*\]")

    @staticmethod
    def split_list_items(item):
        special_list_item = list(ModelAccessor.split(item,
                                                     pattern=SpecialListAccessor.SPLIT_ACCESSOR_REGEX,
                                                     maxsplit=1))
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


class FieldAccessor(object):
    __slots__ = ('access', '_parent_accessor', 'info', '__weakref__')

    __metaclass__ = ABCMeta

    def __init__(self, access, parent_accessor=None, **info):
        self._parent_accessor = parent_accessor
        self.access = access
        self.info = info

    @property
    def field(self):
        try:
            return self._parent_accessor[self.access]
        except Exception as e:
            raise exc.FieldAccessorError(str(e))

    @property
    def parent_accessor(self):
        return self._parent_accessor

    @parent_accessor.setter
    def parent_accessor(self, accessor):
        if isinstance(accessor, ModelAccessor):
            self._parent_accessor = accessor
            return
        raise exc.FieldAccessorError("{} type must be ModelAccessor".format(accessor))

    @abstractmethod
    def set_value(self, value):
        pass

    @abstractmethod
    def get_value(self):
        pass
