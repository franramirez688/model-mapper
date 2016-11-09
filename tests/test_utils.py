import unittest

from modelmapper.utils import ModelAccessor


class ChildA(object):
    value = None

class ChildB(object):
    text = 'Child B'
    books = {'FB': 'First Book'}

class ChildC(object):
    value = [1, 2, 3, 4]

class Children(object):
    child_a = ChildA()
    child_b = ChildB()
    all = [ChildB(), ChildA()]


def get_children_obj():
    return Children()


def get_model_data():
    return {
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
        self._children = get_children_obj()
        self._model_data = get_model_data()

        self._model_data_accessor = ModelAccessor(self._model_data)
        self._children_accessor = ModelAccessor(self._children)

    def test_get_value(self):
        real_value = self._model_data['a']['aa']['aaa']
        self.assertEqual(real_value, self._model_data_accessor['a.aa.aaa'])
        self.assertTrue(self._model_data_accessor.get('a.aa.xbr') is None)

    def test_set_value(self):
        self._model_data_accessor['a.aa.aaa'] = 10
        self._model_data_accessor['a.bb'] = 15

        self.assertTrue(self._model_data['a']['aa']['aaa'] == 10)
        self.assertTrue(self._model_data['a']['bb'] == 15)


    def test_contain_value(self):
        self.assertTrue('a.aa.aaa' in self._model_data_accessor)

    def test_set_value_to_list(self):
        pass

    def test_get_value_from_list(self):
        pass
