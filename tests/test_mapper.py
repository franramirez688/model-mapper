import unittest

from modelmapper.base import ModelMapper
from modelmapper.fields import Field


# class Child(object):
#     name = None
#     age = None
#
# class ChildA(object):
#     value = None
#
#
# class ChildB(object):
#     text = 'Child B'
#     books = {'FB': 'First Book'}
#
#
# class OtherChilds(object):
#     one = ChildA()
#     two = ChildB()
#
#
# class Children(object):
#     child_a = ChildA()
#     child_b = ChildB()
#     child = Child()
#     others = OtherChilds()
#
#
# def get_origin_model():
#     return {
#         'a': {'aa': {'aaa': 7}},
#         'b': 5,
#         'c': [{'c1': 5, 'c2': 7},
#               {'c1': 6, 'c2': 8}],
#         'd': {
#             'd1': 'fake d1',
#             'd2': 'fake d2'
#         }
#     }
#
#
# def get_destination_model():
#     return Children()
#
#
# def get_list_uniform_mapper():
#     return {
#         'name_link': (Field('c1'), Field('name')),
#         'age_link': (Field('c2'), Field('age'))
#     }
#
#
# def get_composed_mapper():
#     return {
#         'one_link': (Field('d1'), Field('one.value')),
#         'two_link': (Field('d2'), Field('two.text'))
#     }
#
# def get_mapper_model():
#     return {
#         'child_a_link': (Field('a.aa.aaa'), Field('child_a.value')),
#         'child_b_link': (Field('a.aa.aaa'), Field('child_a.value')),
#         'child_link': ('c[*]', 'child', get_list_uniform_mapper()),
#         'others_link': ('d', 'others', get_composed_mapper())
#     }
#



class A(object):
    val_a = None


class B(object):
    val_b = None


class C(object):
    val_c = [A(), B()]
    val_cc = None
    val_ccc = A()


class D(object):
    val_d = C()
    val_dd = B()
    val_ddd = A()
    val_dddd = None


def get_origin_model():
    return {
        'd': [
            {
                'c': [
                    {'a': 1},
                    {'b': 1}
                ],
                'cc': 'fake',
                'ccc': [
                    {'a': 1},
                    {'a': 1}
                ]
            },
            {
                'c': [
                    {'a': 2},
                    {'b': 2}
                ],
                'cc': 'fake',
                'ccc': [
                    {'a': 2},
                    {'a': 2}
                ]
            },
        ],
        'dd': {
            'b': {
                'new_val_1': 'fake1',
                'new_val_2': 'fake2'
            }
        },
        'ddd': {
            'a': 1
        },
        'dddd': 1
    }


def get_destination_model():
    return D()


def get_child_x_mapper(x):
    return {
       '{}_link'.format(x): (Field(x), Field('val_{}'.format(x)))
    }


def get_d_mapper():
    return {
        'c_0_link': ('c[0]', 'val_c[0]', get_child_x_mapper('a')),
        'c_1_link': ('c[1]', 'val_c[1]', get_child_x_mapper('b')),
        'cc_link': (Field('cc'), Field('val_cc')),
        'ccc_link': ('ccc[*]', 'val_ccc', get_child_x_mapper('a'))
    }


def get_model_mapper():
    return {
        'd_link': ('d[*]', 'val_d', get_d_mapper()),
        'dd_link': (Field('dd.b'), Field('val_dd.val_b')),
        'ddd_link': (Field('ddd.a'), Field('val_ddd.val_a')),
        'dddd_link': (Field('dddd'), Field('val_dddd')),
    }


def get_model_mapper_verbose():
    return {
        'c_0_link.child_a_link.child_a_link': (Field('d[*].c[0].a'), Field('val_d.val_c[0].val_a')),
        'c_1_link.child_b_link.child_b_link': (Field('d[*].c[1].b'), Field('val_d.val_c[1].val_b')),
        'cc_link': (Field('d[*].cc'), Field('val_d.val_cc')),
        'ccc_link': (Field('d[*].ccc[*]'), Field('val_d.val_ccc.val_a')),
        'dd_link': (Field('dd.b'), Field('val_dd.val_b')),
        'ddd_link': (Field('ddd.a'), Field('val_ddd.val_a')),
        'dddd_link': (Field('dddd'), Field('val_dddd')),
    }


class TestModelMapper(unittest.TestCase):

    def setUp(self):
        self._origin_model = get_origin_model()
        self._destination_model = get_destination_model()
        self._mapper = get_model_mapper()
        self._model_mapper = ModelMapper(self._origin_model, self._destination_model, self._mapper)

    def test_checking_destination_has_the_correct_initial_values(self):
        self._model_mapper.prepare_mapper()
        self._model_mapper.update_destination()

    def test_checking_destination_updates_index_in_uniform_lists_mappers(self):
        self._model_mapper.prepare_mapper()
        self._model_mapper.update_destination()
        self._model_mapper['d_link.ccc_link'].current_index = 1

    def test_checking_origin_loads_data_from_destination(self):
        self._model_mapper.prepare_mapper()
        self._model_mapper.update_origin()
