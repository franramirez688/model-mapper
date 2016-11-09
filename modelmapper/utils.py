import re

from modelmapper.exceptions import ModelAccessorAttributeError, ModelAccessorIndexError, ModelAccessorError


class ModelAccessor(object):

    SPLIT_ACCESSOR_REGEX = re.compile(r"[.\[\]]+")


    def __init__(self, model):
        """
        :param model: dictionary or a simple object
        """
        self._model = model

    def split(self, name, pattern=None):
        pattern = pattern or self.SPLIT_ACCESSOR_REGEX
        return pattern.split(name)

    def get(self, name, default=None):
        try:
            return self.__getitem__(name)
        except ModelAccessorError:
            return default

    def _get_item(self, root_obj, attr):
        if isinstance(root_obj, dict):
            return root_obj[attr]
        elif isinstance(root_obj, (list, tuple)):
            return root_obj[int(attr)]
        else:
            return getattr(root_obj, attr)

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
            try:
                target_item = self._get_item(target_item, item)
            except AttributeError:
                raise ModelAccessorAttributeError("{target} has not the attribute {item}".format(target=target_item, item=item))
            except IndexError:
                raise ModelAccessorIndexError("Not exist the index {index} in {target} object".format(index=item, target=target_item))
            except Exception as e:
                raise ModelAccessorError(str(e))
        return target_item

    def __getitem__(self, item):
        items = self.split(item)
        return self._get_target_item(items) if len(items) > 1 else self._get_item(self._model, item[0])

    def __setitem__(self, item, value):
        items = self.split(item)
        parent_target_item = self._get_target_item(items[:-1]) if len(items) > 1 else self._model
        self._set_item(parent_target_item, items[-1], value)

    def __contains__(self, item):
        try:
            self.__getitem__(item)
            return True
        except ModelAccessorError:
            return  False
