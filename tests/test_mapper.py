import unittest

from modelmapper.fields import Field


class Child(object):
    name = None
    age = None

class ChildA(object):
    value = None


class ChildB(object):
    text = 'Child B'
    books = {'FB': 'First Book'}


class Children(object):
    child_a = ChildA()
    child_b = ChildB()
    child = Child()


def get_origin_model():
    return {
        'a': {'aa': {'aaa': 7}},
        'b': 5,
        'c': [{'c1': 5, 'c2': 7},
              {'c1': 6, 'c2': 8}],
        'd': {
            'd1': 'fake d1',
            'd2': 'fake d2'
        }
    }


def get_destination_model():
    return Children()


def get_list_uniform_mapper():
    return {
        'name_field': (Field('c1'), Field('name')),
        'age_field': (Field('c2'), Field('age'))
    }

def get_mapper_model():
    return {
        'child_a_field': (Field('a.aa.aaa'), Field('child_a.value')),
        'child_b_field': (Field('a.aa.aaa'), Field('child_a.value')),
        'child_field': UniformListMapper('c[*]', 'child', get_list_uniform_mapper())
    }


class TestModelMapper(unittest.TestCase):

    def setUp(self):
        pass
