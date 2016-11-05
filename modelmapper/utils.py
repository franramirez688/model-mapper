"""
    Class based on question from Stackoverflow:
        - http://stackoverflow.com/questions/3797957/python-easily-access-deeply-nested-dict-get-and-set
        - https://gist.github.com/einnocent/8854896
"""
from modelmapper.exceptions import ModelDataAccessorError

# TODO: It must be compatible with list values

class ModelDataAccessor(dict):
    """
        Turn dict into an object that allows access to nested keys via dot notation
    """

    def __init__(self, value=None):
        if isinstance(value, dict):
            for key in value:
                self.__setitem__(key, value[key])
        elif value is not None:
            raise ModelDataAccessorError('Expected dict or NoneType')

    def _is_path(self, k):
        """Check if k is a path to an element of the dictionary

        :param k: key element
        :return:
        """
        return k is not None and '.' in k

    def _check_if_raise_accessor_error(self, root_element, root_key_path, rest_key_path):
        if not isinstance(root_element, ModelDataAccessor):
            raise ModelDataAccessorError('Wrong relation between "{rest_key_path}" with "{root_key_path}"'.format(
                rest_key_path=rest_key_path,
                root_key_path=root_key_path)
            )

    def __setitem__(self, k, val):
        """Set any item with the dict default syntax and the following one:
            model_data['a.b.c'] = 5
            model_data.a.b.c = 5

        :param k: key element
        :param val: key value
        """
        if self._is_path(k):
            root_key_path, rest_key_path = k.split('.', 1)
            root_element = self.setdefault(root_key_path, ModelDataAccessor())
            self._check_if_raise_accessor_error(root_element, root_key_path, rest_key_path)
            root_element[rest_key_path] = val
        else:
            if isinstance(val, dict) and not isinstance(val, ModelDataAccessor):
                val = ModelDataAccessor(val)
            dict.__setitem__(self, k, val)

    def __getitem__(self, k):
        """Get any item with the dict default syntax and the following one:
                val = model_data.a.b.c
                val = model_data.get('a.b.c')

        :param k: key element
        """
        if self._is_path(k):
            root_key_path, rest_key_path = k.split('.', 1)
            root_element = dict.__getitem__(self, root_key_path)
            self._check_if_raise_accessor_error(root_element, root_key_path, rest_key_path)
            return root_element[rest_key_path]
        return dict.__getitem__(self, k)

    def __contains__(self, k):
        """True if ModelDataAccessor has a key k, else False. Valid syntax:
                'a.b.c' in model_data

        :param k: key dict object
        :return: True or False
        """
        if self._is_path(k):
            root_key_path, rest_key_path = k.split('.', 1)
            if not dict.__contains__(self, root_key_path):
                return False
            root_element = dict.__getitem__(self, root_key_path)
            if not isinstance(root_element, ModelDataAccessor):
                return False
            return rest_key_path in root_element
        return dict.__contains__(self, k)

    def setdefault(self, k, d=None):
        if k not in self:
            self[k] = d
        return self[k]

    def get(self, k, d=None):
        if ModelDataAccessor.__contains__(self, k):
            return ModelDataAccessor.__getitem__(self, k)
        return d

    __setattr__ = __setitem__
    __getattr__ = __getitem__
