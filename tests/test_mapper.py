import unittest

from nose_parameterized import parameterized

from modelmapper.base import ModelMapper
from modelmapper.fields import Field


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
                    {'b': 2}
                ],
                'cc': 'fake 1',
                'ccc': [
                    {'a': 1},
                    {'a': 2}
                ]
            },
            {
                'c': [
                    {'a': 3},
                    {'b': 4}
                ],
                'cc': 'fake 2',
                'ccc': [
                    {'a': 3},
                    {'a': 4}
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
       '{}_link'.format(x): (x, 'val_{}'.format(x))
    }


def get_d_mapper():
    return {
        'c_0_link': ('c[0]', 'val_c[0]', get_child_x_mapper('a')),
        'c_1_link': ('c[1]', 'val_c[1]', get_child_x_mapper('b')),
        'cc_link': ('cc', 'val_cc'),
        'ccc_link': ('ccc[*]', 'val_ccc', get_child_x_mapper('a'))
    }


def get_model_mapper():
    return {
        'd_link': ('d[*]', 'val_d', get_d_mapper()),
        'dd_link': ('dd.b', 'val_dd.val_b'),
        'ddd_link': ('ddd.a', 'val_ddd.val_a'),
        'dddd_link': ('dddd', 'val_dddd'),
    }


# def get_model_mapper_verbose():
#     return {
#         'c_0_link.child_a_link.child_a_link': ('d[*].c[0].a', 'val_d.val_c[0].val_a'),
#         'c_1_link.child_b_link.child_b_link': ('d[*].c[1].b', 'val_d.val_c[1].val_b'),
#         'cc_link': ('d[*].cc', 'val_d.val_cc'),
#         'ccc_link': ('d[*].ccc[*]', 'val_d.val_ccc.val_a'),
#         'dd_link': ('dd.b', 'val_dd.val_b'),
#         'ddd_link': ('ddd.a', 'val_ddd.val_a'),
#         'dddd_link': ('dddd', 'val_dddd'),
#     }


class TestModelMapper(unittest.TestCase):

    def setUp(self):
        self._origin_model = get_origin_model()
        self._destination_model = get_destination_model()
        self._mapper = get_model_mapper()
        self._model_mapper = ModelMapper(self._origin_model, self._destination_model, self._mapper)

        self._model_mapper.prepare_mapper()

    def _assert_d_link_values(self, d_link_index=0, ccc_link_index=0, assert_equal=True):
        orig_parent = self._origin_model['d'][d_link_index]
        dest_parent = self._destination_model.val_d
        assert_ = self.assertEqual if assert_equal else self.assertNotEqual

        assert_(orig_parent['c'][0]['a'], dest_parent.val_c[0].val_a)
        assert_(orig_parent['c'][1]['b'], dest_parent.val_c[1].val_b)
        assert_(orig_parent['cc'], dest_parent.val_cc)
        self._assert_ccc_link_values(d_link_index, ccc_link_index, assert_equal)

    def _assert_ccc_link_values(self, d_link_index=0, ccc_link_index=0, assert_equal=True):
        orig_parent = self._origin_model['d'][d_link_index]
        dest_parent = self._destination_model.val_d
        assert_ = self.assertEqual if assert_equal else self.assertNotEqual

        assert_(orig_parent['ccc'][ccc_link_index]['a'], dest_parent.val_ccc.val_a)

    def _compare_origin_vs_destination_values(self, d_link_index=0, ccc_link_index=0, assert_equal=True):
        self._assert_d_link_values(d_link_index, ccc_link_index, assert_equal)

        self.assertEqual(self._origin_model['dd']['b'], self._destination_model.val_dd.val_b)
        self.assertEqual(self._origin_model['ddd']['a'], self._destination_model.val_ddd.val_a)
        self.assertEqual(self._origin_model['dddd'], self._destination_model.val_dddd)

    def test_destination_loads_data_from_origin(self):
        self._model_mapper.update_destination()
        self._compare_origin_vs_destination_values()

    @parameterized.expand([
        ("values are equal", 1, True),
        ("values are not equal", 0, False)
    ])
    def test_destination_updates_index_in_uniform_lists_mappers(self, _, ccc_link_index, assert_equal):
        self._model_mapper.update_destination()
        self._model_mapper['d_link.ccc_link'].current_index = 1
        self._assert_ccc_link_values(ccc_link_index=ccc_link_index, assert_equal=assert_equal)

    def test_origin_loads_data_from_destination(self):
        self._destination_model.val_dd.val_b = "New fake value 1"
        self._destination_model.val_ddd.val_a = "New fake value 2"
        self._destination_model.val_dddd = "New fake value 3"
        self._model_mapper.update_origin()
        self._compare_origin_vs_destination_values()
