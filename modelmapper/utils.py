import re

from modelmapper import exceptions


def handle_exceptions(get_or_set):
    def handle(*args, **kwargs):
        root = args[0]
        attr = args[1]
        try:
            return get_or_set(*args, **kwargs)
        except AttributeError:
            raise exceptions.FieldAccessorAttributeError(
                "{root} has not the attribute {attr}".format(root=root, attr=attr))
        except IndexError:
            raise exceptions.FieldAccessorIndexError(
                "Not exist the index {index} in {root} object".format(index=attr, root=root))
        except KeyError:
            raise exceptions.FieldAccessorKeyError(
                "{root} has not the key {attr}".format(root=root, attr=attr))
        except Exception as e:
            raise exceptions.FieldAccessorError(str(e))
    return handle


class FieldAccessor(object):

    SPLIT_ACCESSOR_REGEX = re.compile(r"[.\[\]]+")

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
        except exceptions.FieldAccessorError:
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

    def __getitem__(self, item):
        split_item = self.split(item)
        return self._get_target_item(split_item) if len(split_item) > 1 else self._get_item(self._model, split_item[0])

    def __setitem__(self, item, value):
        split_item = self.split(item)
        parent_target_item = self._get_target_item(split_item[:-1]) if len(split_item) > 1 else self._model
        self._set_item(parent_target_item, split_item[-1], value)

    def __contains__(self, item):
        try:
            self.__getitem__(item)
        except exceptions.FieldAccessorError:
            return False
        else:
            return True


class ModelContainer(object):

        def __init__(self):
            self._cached_objects = None

# class FieldDictAccessor(FieldAccessor):
#
#     @handle_exceptions
#     def _get_item(self, root_obj, attr):
#         return root_obj[int(attr)]
#
#     @handle_exceptions
#     def _set_item(self, root_obj, attr, value):
#         root_obj[attr] = value
#
#
# class FieldListAccessor(FieldAccessor):
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
#         raise exceptions.FieldAccessorAssignmentError("'tuple' object does not support item assignment")
