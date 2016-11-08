import re


class ModelAccessor(object):

    PATH_SEPARATOR_CHARACTER = '.'
    SPLIT_PATTERN = re.compile("\.|\[([0-9]+)\]")

    # >> > pattern = re.compile("\.|\[([0-9]+)\]")
    # >> > pattern.split(a)
    # ['a', None, 'b', None, 'c', '0', '', None, 'd']

    # >> > pattern = re.compile("\.|[\[-\]]+")
    # >> > pattern.split(a)
    # ['a', 'b', 'c', '0', '', 'd']

    def __init__(self, model):
        """
        :param model: dictionary or a simple object
        """
        self._model = model

    def get(self, name, default=None):
        pass

    def _get(self, item, attr_name):
        if isinstance(item, dict):
            return item[attr_name]
        elif isinstance(item, list) and isinstance(int(attr_name)):
            return item[int(attr_name)]
        else:
            return getattr(item, attr_name)

    def _get_target_element(self, items):
        if len(items) > 0:
            target_element = self._model
            for item in items:
                try:
                    target_element = getattr(target_element, item)
                except AttributeError:
                    raise Exception("{target} has not the attribute {item}".format(target=target_element, item=item))
            return target_element
        raise Exception("Items can not be empty")

    def __getattr__(self, item):
        if self.PATH_SEPARATOR_CHARACTER in item:
            items = item.split(self.PATH_SEPARATOR_CHARACTER)
            return self._get_target_element(items)
        return getattr(self._model, item)

    def __setattr__(self, key, value):
        if self.PATH_SEPARATOR_CHARACTER in key:
            items = key.split(self.PATH_SEPARATOR_CHARACTER)
            target_element = self._get_target_element(items[:-1])
            setattr(target_element, items[-1], value)
            return
        setattr(self._model, key, value)

    def __contains__(self, item):
        pass