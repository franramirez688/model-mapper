import unittest

from nose_parameterized import parameterized

from modelmapper.core import ModelMapper
from modelmapper.accessors import FieldAccessor


class A(object):

    def __init__(self, **kwargs):
        self.set_all(**kwargs)

    def set_all(self, a=None, aa=None, aaa=None):
        self.val_a = a
        self.val_aa = aa
        self.val_aaa = aaa

    def get_all(self):
        return {'a': self.val_a, 'aa': self.val_aa, 'aaa': self.val_aaa}


class B(object):
    val_b = None


class C(object):
    val_c = [A(), B()]
    val_cc = None
    val_ccc = A()


class Complex(object):

    def __init__(self):
        self._val = None

    def set_val(self, value):
        self._val = value

    def get_val(self):
        return self._val


class D(object):
    val_d = C()
    val_dd = B()
    val_ddd = A()
    val_dddd = None
    val_complex = Complex()
    val_list = [A(),
                A(),
                A()]


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
        'dddd': 1,
        'complex': "fake1",
        'd_list': [
            {'a': 1, 'aa': [1, 2], 'aaa': "fake aaa 1"},
            {'a': 2, 'aa': [2, 3], 'aaa': "fake aaa 2"},
            {'a': 3, 'aa': [4, 5], 'aaa': "fake aaa 3"}
        ]
    }


class ComplexAccessor(FieldAccessor):

    def get_value(self):
        return self.field.get_val()

    def set_value(self, value):
        self.field.set_val(value)


def get_destination_model():
    return D()


def get_child_x_mapper(x):
    return {
       '{}_link'.format(x): (x, 'val_{}'.format(x))
    }


def get_d_list_mapper():
    return {
        'a_link': ('a', 'val_a'),
        'aa_link': ('aa', 'val_aa'),
        'aaa_link': ('aaa', 'val_aaa')
    }


def get_d_mapper():
    return {
        'c_0_link': ('c[0]', 'val_c[0]', get_child_x_mapper('a')),
        'c_1_link': ('c[1]', 'val_c[1]', get_child_x_mapper('b')),
        'cc_link': ('cc', 'val_cc'),
        'ccc_link': ('ccc', 'val_ccc', get_child_x_mapper('a'))  # UniformList
    }


def get_model_mapper():
    return {
        'd_link': ('d', 'val_d', get_d_mapper()),  # UniformList
        'dd_link': ('dd.b', 'val_dd.val_b'),
        'ddd_link': ('ddd.a', 'val_ddd.val_a'),
        'dddd_link': ('dddd', 'val_dddd'),
        'complex_link': ('complex', ComplexAccessor('val_complex')),
        'list_link': ('d_list', 'val_list', get_d_list_mapper())
    }


class TestModelMapper(unittest.TestCase):

    def setUp(self):
        self._origin_model = get_origin_model()
        self._destination_model = get_destination_model()
        self._mapper = get_model_mapper()

        self._model_mapper = ModelMapper(self._origin_model, self._destination_model, self._mapper)
        self._model_mapper.prepare_mapper()

    def test_destination_loads_data_from_origin(self):
        self._model_mapper.update_destination()
        self._assert_all()

    def test_origin_loads_data_from_destination(self):
        self._initialize_destination_values()
        self._model_mapper.update_origin()
        self._assert_all()

    @parameterized.expand([
        ("values are equal", 1, True),
        ("values are not equal", 0, False)
    ])
    def test_destination_updates_index_in_child_uniform_lists_mappers(self, _, ccc_link_index, assert_equal):
        self._model_mapper.update_destination()
        self._model_mapper['d_link.ccc_link'].current_index = 1
        self._assert_child_uniform_model_list_values(ccc_link_index=ccc_link_index, assert_equal=assert_equal)

    @parameterized.expand([
        ("values are equal", 1, True),
        ("values are not equal", 0, False)
    ])
    def test_destination_updates_index_in_parent_uniform_lists_mappers(self, _, d_link_index, assert_equal):
        self._model_mapper.update_destination()
        self._model_mapper['d_link'].current_index = 1
        self._assert_parent_uniform_model_list_values(d_link_index=d_link_index, assert_equal=assert_equal)
        self._assert_child_uniform_model_list_values(d_link_index=d_link_index, assert_equal=assert_equal)

    def _initialize_destination_values(self):
        self._destination_model.val_d.val_c[0].val_a = "New test val_d.val_c[0].val_a"
        self._destination_model.val_d.val_c[1].val_b = "New test val_d.val_c[1].val_b"
        self._destination_model.val_d.val_cc = "New test val_d.val_cc"
        self._destination_model.val_d.val_ccc.val_a = "New test val_d.val_ccc.val_a"
        self._destination_model.val_dd.val_b = "New test val_dd.val_b"
        self._destination_model.val_ddd.val_a = "New test val_ddd.val_a"
        self._destination_model.val_dddd = "New test val_dddd"
        self._destination_model.val_complex.set_val("New test val_complex")
        self._destination_model.val_list[0] = A(**{'a': 4, 'aa': [], 'aaa': "1"})
        self._destination_model.val_list[1] = A(**{'a': 5, 'aa': [1], 'aaa': "2"})
        self._destination_model.val_list[2] = A(**{'a': 6, 'aa': [1, 2], 'aaa': "3"})

    def _assert_all(self):
        self._assert_root_basic_values()

        self._assert_parent_uniform_model_list_values()
        self._assert_child_uniform_model_list_values()
        self._assert_child_uniform_model_list_values(ccc_link_index=1, assert_equal=False)

        self._assert_parent_uniform_model_list_values(d_link_index=1, assert_equal=False)
        self._assert_child_uniform_model_list_values(d_link_index=1, ccc_link_index=0, assert_equal=False)
        self._assert_child_uniform_model_list_values(d_link_index=1, ccc_link_index=1, assert_equal=False)
        self._assert_model_list_values()

    def _assert_model_list_values(self, assert_equal=True):
        assert_ = self._get_assert(assert_equal)

        for i, orig_item in enumerate(self._origin_model['d_list']):
            assert_(orig_item, self._destination_model.val_list[i].get_all())

    def _assert_parent_uniform_model_list_values(self, d_link_index=0, assert_equal=True):
        orig_parent = self._origin_model['d'][d_link_index]
        dest_parent = self._destination_model.val_d
        assert_ = self._get_assert(assert_equal)

        assert_(orig_parent['c'][0]['a'], dest_parent.val_c[0].val_a)
        assert_(orig_parent['c'][1]['b'], dest_parent.val_c[1].val_b)
        assert_(orig_parent['cc'], dest_parent.val_cc)

    def _assert_child_uniform_model_list_values(self, d_link_index=0, ccc_link_index=0, assert_equal=True):
        orig_parent = self._origin_model['d'][d_link_index]
        dest_parent = self._destination_model.val_d
        assert_ = self._get_assert(assert_equal)

        assert_(orig_parent['ccc'][ccc_link_index]['a'], dest_parent.val_ccc.val_a)

    def _assert_root_basic_values(self, assert_equal=True):
        assert_ = self._get_assert(assert_equal)

        assert_(self._origin_model['dd']['b'], self._destination_model.val_dd.val_b)
        assert_(self._origin_model['ddd']['a'], self._destination_model.val_ddd.val_a)
        assert_(self._origin_model['dddd'], self._destination_model.val_dddd)
        assert_(self._origin_model['complex'], self._destination_model.val_complex.get_val())

    def _get_assert(self, equal=True):
        return self.assertEqual if equal else self.assertNotEqual