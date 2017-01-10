import json
import unittest

from nose_parameterized import parameterized

from modelmapper.accessors import ModelAccessor, FieldAccessor
from modelmapper import exceptions


class ChildA(object):
    value = None


class ChildB(object):
    text = 'Child B'
    books = {'FB': 'First Book'}


class ChildC(object):
    value = [1, 2, 3, 4]


class ChildD(object):

    def __init__(self):
        self._text = None

    @property
    def text(self):
        return self._text

    def set_text(self, value):
        self._text = value


class Children(object):
    child_a = ChildA()
    child_b = ChildB()
    all = [ChildB(), ChildA()]


class FieldChildD(FieldAccessor):

    def __init__(self):
        super(FieldChildD, self).__init__('b')

    def set_value(self, value):
        self.access_object.set_text(value)

    def get_value(self):
        return self.access_object.text


def get_children_obj():
    return Children()


def get_model_dict_data():
    return {
        'a': {'aa': {'aaa': 7}},
        'b': 5,
        'c': [{'c1': 5, 'c2': 7},
              {'c1': 6, 'c2': 8}],
    }


def get_model_list_data():
    return [
        {
            'a': {'aa': {'aaa': 7}},
            'b': 5,
        },
        {
            'a': {'aa': {'aaa': 7}},
            'b': 5,
        },

    ]


class TestModelDataAccessor(unittest.TestCase):

    def setUp(self):
        self._children = get_children_obj()
        self._model_dict_data = get_model_dict_data()
        self._model_list_data = get_model_list_data()

        self._model_dict_data_accessor = ModelAccessor(self._model_dict_data)
        self._model_list_data_accessor = ModelAccessor(self._model_list_data)
        self._children_accessor = ModelAccessor(self._children)

    def test_get_value_from_accessor_list(self):
        self.assertEqual(self._model_list_data[0]['a']['aa']['aaa'], self._model_list_data_accessor['[0].a.aa.aaa'])
        self.assertTrue(self._model_list_data_accessor.get('[0].a.aa.xbr') is None)
        self.assertEqual(self._model_list_data[1]['b'], self._model_list_data_accessor['[1].b'])

    def test_get_value_from_accessor_dict(self):
        self.assertEqual(self._model_dict_data['a']['aa']['aaa'], self._model_dict_data_accessor['a.aa.aaa'])
        self.assertTrue(self._model_dict_data_accessor.get('a.aa.xbr') is None)
        self.assertEqual(self._model_dict_data['b'], self._model_dict_data_accessor['b'])
        self.assertEqual(self._model_dict_data['c'][1]['c1'], self._model_dict_data_accessor['c[1].c1'])
        self.assertEqual(self._model_dict_data['c'][0], self._model_dict_data_accessor['c[0]'])

    @parameterized.expand([
        (exceptions.ModelAccessorKeyError, 'a.xx'),
        (exceptions.ModelAccessorIndexError, 'c[9]'),
        (exceptions.ModelAccessorKeyError, 'c[0].xx')
    ])
    def test_get_value_from_accessor_dict_errors(self, e, name):
        with self.assertRaises(e):
            self._model_dict_data_accessor[name]

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

    def test_set_value_from_list_of_accessor_dict(self):
        self._model_list_data_accessor['[0].a.aa.aaa'] = 10
        self._model_list_data_accessor['[0].a.bb'] = 15
        self._model_list_data_accessor['[1].b'] = 25
        self._model_list_data_accessor['[1].c'] = [1, 2, 3, 4]

        self.assertEqual(self._model_list_data[0]['a']['aa']['aaa'], 10)
        self.assertEqual(self._model_list_data[0]['a']['bb'], 15)
        self.assertEqual(self._model_list_data[1]['b'], 25)
        self.assertEqual(self._model_list_data[1]['c'], [1, 2, 3, 4])

    def test_set_value_from_accessor_dict(self):
        self._model_dict_data_accessor['a.aa.aaa'] = 10
        self._model_dict_data_accessor['a.aa.bbb'] = 10  # create a new one
        self._model_dict_data_accessor['a.bb'] = 15
        self._model_dict_data_accessor['b'] = 25
        self._model_dict_data_accessor['c'] = [1, 2, 3, 4]

        self.assertEqual(self._model_dict_data['a']['aa']['aaa'], 10)
        self.assertEqual(self._model_dict_data['a']['aa']['bbb'], 10)
        self.assertEqual(self._model_dict_data['a']['bb'], 15)
        self.assertEqual(self._model_dict_data['b'], 25)
        self.assertEqual(self._model_dict_data['c'], [1, 2, 3, 4])

    def test_set_value_from_accessor_object(self):
        self._children_accessor['child_a.value'] = 10
        self._children_accessor['child_b.books.FB'] = "New value book"
        self._children_accessor['all[1].value'] = 25

        self.assertEqual(self._children.child_a.value, 10)
        self.assertEqual(self._children.child_b.books['FB'], "New value book")
        self.assertEqual(self._children.all[1].value, 25)

    def test_contain_value_in_dict(self):
        self.assertTrue('a.aa.aaa' in self._model_dict_data_accessor)
        self.assertTrue('b' in self._model_dict_data_accessor)
        self.assertTrue('a.xx' not in self._model_dict_data_accessor)
        self.assertTrue('c[0].c1' in self._model_dict_data_accessor)
        self.assertTrue('c[3]' not in self._model_dict_data_accessor)

    def test_contain_value_in_object(self):
        self.assertTrue('child_a' in self._children_accessor)
        self.assertTrue('child_c' not in self._children_accessor)
        self.assertTrue('all[1].value' in self._children_accessor)
        self.assertTrue('all[0].books.FB' in self._children_accessor)

    def test_special_character_list_in_simple_get_item(self):
        self.assertEqual(self._model_dict_data['c'], self._model_dict_data_accessor['c[*]'])

    def test_special_character_list_in_complex_get_item(self):
        expected = []
        for item in self._model_dict_data['c']:
            expected.append(item['c1'])
        self.assertEqual(expected, self._model_dict_data_accessor['c[*].c1'])

    def test_special_character_list_in_simple_set_item(self):
        self._model_dict_data_accessor['c[*]'] = [1, 2]
        self.assertEqual(self._model_dict_data['c'], [1, 2])

    def test_special_character_list_in_complex_set_item(self):
        self._model_dict_data_accessor['c[*].c1'] = 1
        for item in self._model_dict_data['c']:
            self.assertEqual(item['c1'], 1)


class TestPerformanceModelAccessor(unittest.TestCase):

    def setUp(self):
        dict_var_name = 'more_longer_name'
        self._num_recursion = 256
        data = TestPerformanceModelAccessor.create_massive_model(dict_var_name, self._num_recursion)
        self._model_accessor = ModelAccessor(data)
        self._item_access = '.'.join([dict_var_name] * self._num_recursion)

    def test_performance_in_get_item(self):
        for _ in range(5):
            self.assertEqual(self._model_accessor[self._item_access], self._num_recursion)

    def test_performance_in_set_item(self):
        for _ in range(4):
            self._model_accessor[self._item_access] = 8
        self.assertEqual(self._model_accessor[self._item_access], 8)

    @staticmethod
    def create_massive_model(dict_var_name, num_recursion):
        data = ['{{"{}": '.format(dict_var_name)] * num_recursion
        data.append("{}".format(num_recursion))
        data.append("}" * num_recursion )
        return json.loads(''.join(data))