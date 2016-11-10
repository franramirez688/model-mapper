import re

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

    def __init__(self, model):
        """
        :param model: dictionary or a simple object
        """
        self._model = model

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
        for item in items:
            target_item = self._get_item(target_item, item)
        return target_item

    def __getitem__(self, item):
        items = self.split(item)
        return self._get_target_item(items) if len(items) > 1 else self._get_item(self._model, items[0])

    def __setitem__(self, item, value):
        items = self.split(item)
        parent_target_item = self._get_target_item(items[:-1]) if len(items) > 1 else self._model
        self._set_item(parent_target_item, items[-1], value)

    def __contains__(self, item):
        try:
            self.__getitem__(item)
            return True
        except exceptions.ModelAccessorError:
            return False
