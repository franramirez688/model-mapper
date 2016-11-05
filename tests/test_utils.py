import unittest

from modelmapper.utils import ModelDataAccessor

model_data_dict = {
    'a': {
        'aa': {
            'aaa': 7
        },
    'b': 5,
    'c': [
            {'c1': 5, 'c2': 7},
            {'c1': 6, 'c2': 8},
         ]
    }
}


class TestModelDataAccessor(unittest.TestCase):

    def setUp(self):
        self._model_data_accessor = ModelDataAccessor(model_data_dict)

    def test_get_value(self):
        pass

    def test_set_value(self):
        pass

    def test_contain_value(self):
        pass

    def test_set_value_to_list(self):
        pass

    def test_get_value_from_list(self):
        pass
