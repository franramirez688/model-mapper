import unittest

from nose_parameterized import parameterized

from modelmapper.core import ModelMapper, ListModelMapper
from tests.destination_data import get_destination_model, A
from tests.mapper_data import get_model_mapper, get_list_model_mapper
from tests.origin_data import get_origin_model


class TestCompleteModelMapper(unittest.TestCase):

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
        self._model_mapper['d_link.ccc_link'].index = 1
        self._assert_child_uniform_list_model_values(ccc_link_index=ccc_link_index, assert_equal=assert_equal)

    @parameterized.expand([
        ("values are equal", 1, True),
        ("values are not equal", 0, False)
    ])
    def test_destination_updates_index_in_parent_uniform_lists_mappers(self, _, d_link_index, assert_equal):
        self._model_mapper.update_destination()
        self._model_mapper['d_link'].index = 1
        self._assert_parent_uniform_list_model_values(d_link_index=d_link_index, assert_equal=assert_equal)
        self._assert_child_uniform_list_model_values(d_link_index=d_link_index, assert_equal=assert_equal)

    def _initialize_destination_values(self):
        dest = self._destination_model
        dest.val_d.val_c[0].val_a = "New test val_d.val_c[0].val_a"
        dest.val_d.val_c[1].val_b = "New test val_d.val_c[1].val_b"
        dest.val_d.val_cc = "New test val_d.val_cc"
        dest.val_d.val_ccc.val_a = "New test val_d.val_ccc.val_a"
        dest.val_dd.val_b = "New test val_dd.val_b"
        dest.val_ddd.val_a = "New test val_ddd.val_a"
        dest.val_dddd = "New test val_dddd"
        dest.val_complex.set_val("New test val_complex")
        dest.val_list[0] = A(**{'a': 4, 'aa': [], 'aaa': "1"})
        dest.val_list[1] = A(**{'a': 5, 'aa': [1], 'aaa': "2"})
        dest.val_list[2] = A(**{'a': 6, 'aa': [1, 2], 'aaa': "3"})
        # dest.val_list.append(A(**{'a': 7, 'aa': [3, 4], 'aaa': "4"}))

    def _assert_all(self):
        self._assert_root_basic_values()

        self._assert_parent_uniform_list_model_values()
        self._assert_child_uniform_list_model_values()
        self._assert_child_uniform_list_model_values(ccc_link_index=1, assert_equal=False)

        self._assert_parent_uniform_list_model_values(d_link_index=1, assert_equal=False)
        self._assert_child_uniform_list_model_values(d_link_index=1, ccc_link_index=0, assert_equal=False)
        self._assert_child_uniform_list_model_values(d_link_index=1, ccc_link_index=1, assert_equal=False)

        self._assert_list_model_values()

    def _assert_list_model_values(self, assert_equal=True):
        assert_ = self._get_assert(assert_equal)

        for i, orig_item in enumerate(self._origin_model['d_list']):
            assert_(orig_item, self._destination_model.val_list[i].get_all())

    def _assert_parent_uniform_list_model_values(self, d_link_index=0, assert_equal=True):
        orig_parent = self._origin_model['d'][d_link_index]
        dest_parent = self._destination_model.val_d
        assert_ = self._get_assert(assert_equal)

        assert_(orig_parent['c'][0]['a'], dest_parent.val_c[0].val_a)
        assert_(orig_parent['c'][1]['b'], dest_parent.val_c[1].val_b)
        assert_(orig_parent['cc'], dest_parent.val_cc)

    def _assert_child_uniform_list_model_values(self, d_link_index=0, ccc_link_index=0, assert_equal=True):
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
