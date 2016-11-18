import unittest

from nose_parameterized import parameterized

from modelmapper.utils import ModelAccessor
from modelmapper import exceptions


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
        'a': {'aa': {'aaa': 7}},
        'b': 5,
        'c': [{'c1': 5, 'c2': 7},
              {'c1': 6, 'c2': 8}]
    }


class TestModelDataAccessor(unittest.TestCase):

    def setUp(self):
        self._children = get_children_obj()
        self._model_data = get_model_data()

        self._model_data_accessor = ModelAccessor(self._model_data)
        self._children_accessor = ModelAccessor(self._children)

    def test_get_value_from_accessor_dict(self):
        self.assertEqual(self._model_data['a']['aa']['aaa'], self._model_data_accessor['a.aa.aaa'])
        self.assertTrue(self._model_data_accessor.get('a.aa.xbr') is None)
        self.assertEqual(self._model_data['b'], self._model_data_accessor['b'])
        self.assertEqual(self._model_data['c'][1]['c1'], self._model_data_accessor['c[1].c1'])
        self.assertEqual(self._model_data['c'][0], self._model_data_accessor['c[0]'])

    @parameterized.expand([
        (exceptions.ModelAccessorKeyError, 'a.xx'),
        (exceptions.ModelAccessorIndexError, 'c[9]'),
        (exceptions.ModelAccessorKeyError, 'c[0].xx')
    ])
    def test_get_value_from_accessor_dict_errors(self, e, name):
        with self.assertRaises(e):
            self._model_data_accessor[name]

    @parameterized.expand([
        (exceptions.ModelAccessorIndexError, 'all[5]'),
        (exceptions.ModelAccessorAttributeError, 'child_b.fake')
    ])
    def test_get_value_from_accessor_dict_errors(self, e, name):
        with self.assertRaises(e):
            self._children_accessor[name]

    def test_get_value_from_accessor_object(self):
        self.assertEqual(self._children.child_b.books, self._children_accessor['child_b.books'])
        self.assertEqual(self._children.all, self._children_accessor['all'])
        self.assertEqual(self._children.all[0].text, self._children_accessor['all[0].text'])
        self.assertEqual(self._children.all[0].books['FB'], self._children_accessor['all[0].books.FB'])

    def test_set_value_from_accessor_dict(self):
        self._model_data_accessor['a.aa.aaa'] = 10
        self._model_data_accessor['a.bb'] = 15
        self._model_data_accessor['b'] = 25

        self.assertEqual(self._model_data['a']['aa']['aaa'], 10)
        self.assertEqual(self._model_data['a']['bb'], 15)
        self.assertEqual(self._model_data['b'], 25)

    def test_set_value_from_accessor_object(self):
        self._children_accessor['child_a.value'] = 10
        self._children_accessor['child_b.books.FB'] = "New value book"
        self._children_accessor['all[1].value'] = 25

        self.assertEqual(self._children.child_a.value, 10)
        self.assertEqual(self._children.child_b.books['FB'], "New value book")
        self.assertEqual(self._children.all[1].value, 25)

    def test_contain_value_in_dict(self):
        self.assertTrue('a.aa.aaa' in self._model_data_accessor)
        self.assertTrue('b' in self._model_data_accessor)
        self.assertTrue('a.xx' not in self._model_data_accessor)
        self.assertTrue('c[0].c1' in self._model_data_accessor)
        self.assertTrue('c[3]' not in self._model_data_accessor)

    def test_contain_value_in_object(self):
        self.assertTrue('child_a' in self._children_accessor)
        self.assertTrue('child_c' not in self._children_accessor)
        self.assertTrue('all[1].value' in self._children_accessor)
        self.assertTrue('all[0].books.FB' in self._children_accessor)
